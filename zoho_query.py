from dotenv import load_dotenv
import os
import json
from groq import Groq
from zohocrmsdk.src.com.zoho.api.authenticator.oauth_token import OAuthToken
from zohocrmsdk.src.com.zoho.crm.api.initializer import Initializer
from zohocrmsdk.src.com.zoho.crm.api.dc import INDataCenter
from zohocrmsdk.src.com.zoho.crm.api.sdk_config import SDKConfig
from zohocrmsdk.src.com.zoho.crm.api.record import RecordOperations, GetRecordsHeader, GetRecordsParam
from zohocrmsdk.src.com.zoho.crm.api.parameter_map import ParameterMap
from zohocrmsdk.src.com.zoho.crm.api.util import Choice

class ZohoCRMQueryProcessor:
    def __init__(self):
        load_dotenv()
        self.groq_client = Groq(
            api_key=os.getenv("GROQ_API_KEY")
        )
        
        # Initialize Zoho CRM SDK
        self._initialize_zoho()
        
    def _initialize_zoho(self):
        """Initialize Zoho CRM SDK with OAuth credentials"""
        try:
            # Get credentials from .env file
            client_id = os.getenv("ZOHO_CLIENT_ID")
            client_secret = os.getenv("ZOHO_CLIENT_SECRET")
            refresh_token = os.getenv("ZOHO_REFRESH_TOKEN")
            
            # Create an instance of Token
            token = OAuthToken(
                client_id=client_id,
                client_secret=client_secret,
                refresh_token=refresh_token
            )
            
            # The scope is set when generating the refresh token, not here in the SDK
            print("Using refresh token with scopes: ZohoCRM.modules.ALL, ZohoCRM.settings.ALL")

            # Create an instance of SDKConfig
            sdk_config = SDKConfig(
                auto_refresh_fields=True,
                pick_list_validation=False
            )

            # The path containing the absolute directory path to store user specific JSON files
            resource_path = os.path.join(os.getcwd(), 'resources')
            
            # Create the directory if it doesn't exist
            if not os.path.exists(resource_path):
                os.makedirs(resource_path)

            # Initialize the SDK
            Initializer.initialize(
                environment=INDataCenter.PRODUCTION(),
                token=token,
                sdk_config=sdk_config,
                resource_path=resource_path
            )
            print("Zoho CRM SDK initialized successfully!")
            
        except Exception as e:
            print(f"Error initializing Zoho SDK: {str(e)}")
            raise

    def _convert_to_api_query(self, natural_query: str) -> dict:
        """Convert natural language to Zoho CRM API query format"""
        system_prompt = """
        You are a Zoho CRM expert. Convert natural language to Zoho CRM API query parameters.
        Output must be a valid JSON with these possible keys:
        - module: The CRM module to query (Leads, Contacts, Deals, etc.)
        - fields: List of fields to retrieve
        - criteria: Filter criteria in Zoho format ((field:operator:value) and/or (field:operator:value))
        - sort_by: Field to sort by
        - sort_order: asc or desc
        - page: Page number (default: 1)
        - per_page: Records per page (default: 200)
        -output ONLY valid JSON with no additional text or punctuation marks like ``` or ```
        """

        try:
            completion = self.groq_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Convert this query: {natural_query}"}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            raw_response = completion.choices[0].message.content
            print(f"Generated API Query: {raw_response}")
            
            try:
                api_query = json.loads(raw_response)
                return api_query
            except json.JSONDecodeError as e:
                raise Exception(f"Failed to parse LLM response as JSON: {str(e)}")
                
        except Exception as e:
            raise Exception(f"Error in query conversion: {str(e)}")

    def _execute_api_query(self, query_params: dict) -> dict:
        """Execute query against Zoho CRM using the REST API
        
        Args:
            query_params (dict): Dictionary containing:
                - module (str): The CRM module to query (required)
                - fields (list): List of fields to retrieve
                - criteria (str): Filter criteria
                - sort_by (str): Field to sort by
                - sort_order (str): Sort order (asc/desc)
                - page (int): Page number
                - per_page (int): Records per page
        
        Returns:
            dict: Query results or error message
        """
        try:
            # Create instance of RecordOperations with module name
            module_api_name = query_params.get('module')
            if not module_api_name:
                raise ValueError("Module name is required")
                
            record_operations = RecordOperations(module_api_name)
            param_instance = ParameterMap()
            
            # Add fields parameter if specified
            if query_params.get('fields'):
                param_instance.add(GetRecordsParam.fields, ','.join(query_params['fields']))
            
            # Add criteria if specified
            if query_params.get('criteria'):
                # Format criteria according to Zoho's syntax: ((field:operator:value))
                raw_criteria = query_params['criteria']
                # Check if criteria already has the proper format
                if not (raw_criteria.startswith('((') and raw_criteria.endswith('))')):
                    # If not properly formatted, wrap it in double parentheses
                    formatted_criteria = f"(({raw_criteria}))"
                else:
                    formatted_criteria = raw_criteria
                    
                param_instance.add(GetRecordsParam.criteria, formatted_criteria)            

            # Add sorting if specified
            if query_params.get('sort_by'):
                param_instance.add(GetRecordsParam.sort_by, query_params['sort_by'])
                sort_order = query_params.get('sort_order', 'desc')
                param_instance.add(GetRecordsParam.sort_order, sort_order)
            
            # Add pagination parameters
            page = query_params.get('page', 1)
            per_page = min(query_params.get('per_page', 200), 200)
            param_instance.add(GetRecordsParam.page, page)
            param_instance.add(GetRecordsParam.per_page, per_page)
            
            # Get records
            response = record_operations.get_records(param_instance)
            
            if not response:
                return {
                    'status': 'error',
                    'message': 'No response from Zoho CRM'
                }

            status_code = response.get_status_code()
            
            # Handle empty responses
            if status_code in [204, 304]:
                return {
                    'status': 'success',
                    'records': [],
                    'count': 0,
                    'more_records': False
                }

            try:
                response_object = response.get_object()
                if not response_object:
                    return {
                        'status': 'error',
                        'message': 'Invalid response format from Zoho CRM'
                    }

                # Handle API exceptions
                if hasattr(response_object, 'status') and response_object.status.lower() == 'error':
                    return {
                        'status': 'error',
                        'message': f'Zoho API Error: {response_object.message if hasattr(response_object, "message") else "Unknown error"}'
                    }

                if isinstance(response_object, Choice):
                    response_object = response_object.get_value()

                records = []
                if hasattr(response_object, 'get_data'):
                    records = response_object.get_data() or []

                info = None
                if hasattr(response_object, 'get_info'):
                    info = response_object.get_info()

                processed_records = []
                for record in records:
                    try:
                        record_dict = {}
                        for key, value in record.get_key_values().items():
                            if isinstance(value, Choice):
                                value = value.get_value()
                            record_dict[key] = str(value) if value is not None else None
                        processed_records.append(record_dict)
                    except Exception as record_error:
                        print(f"Error processing record: {str(record_error)}")
                        continue

                return {
                    'status': 'success',
                    'records': processed_records,
                    'count': len(processed_records),
                    'more_records': info.get_more_records() if info else False
                }
                
            except Exception as processing_error:
                print(f"Error processing response: {str(processing_error)}")
                return {
                    'status': 'error',
                    'message': f'Error processing response: {str(processing_error)}'
                }

        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error executing API query: {str(e)}'
            }

    def process_query(self, natural_query: str) -> dict:
        """Process natural language query and return results"""
        try:
            print(f"\nProcessing natural language query: {natural_query}")
            
            api_query = self._convert_to_api_query(natural_query)
            results = self._execute_api_query(api_query)
            
            return {
                'status': 'success',
                'query_details': api_query,
                'results': results
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

def query_zoho_crm(natural_query: str) -> dict:
    """Helper function for Flask app"""
    try:
        processor = ZohoCRMQueryProcessor()
        return processor.process_query(natural_query)
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error processing query: {str(e)}'
        }