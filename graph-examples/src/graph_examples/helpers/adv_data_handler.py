from graph_examples.helpers.params import DatabaseParams, SurrealParams
from graph_examples.helpers.ux_helpers import *
from surrealdb import AsyncSurreal



class ADVDataHandler():
   
    def __init__(self, connection: AsyncSurreal):
        self.connection = connection
    


# SELECT assets_under_management,custodian_type,source_filing,in.identifier,in.name,out.identifier,out.name FROM custodian_for
# WHERE custodian_type = custodian_type:SMA;
# SELECT description,custodian_type,source_filing,in.identifier,in.name,out.identifier,out.name FROM custodian_for
# WHERE custodian_type = custodian_type:⟨A third-party unaffiliated record keeper⟩
# AND (description @1@ 'cloud' OR description @2@ 'data') AND in != out;


    async def get_custodian_graph(self, custodian_type:str = None, 
                                  description_matches:list[str] = None, 
                                  order_by:str = None,
                                  limit:int = None):
        
        where_clause = ""
        params = {}
        if custodian_type:
            if where_clause:
                where_clause += " AND "
            where_clause += " custodian_type = type::thing('custodian_type',$custodian_type)"
            params["custodian_type"] = custodian_type

        if description_matches:
            if where_clause:
                where_clause += " AND ("
            match_index = 1
            where_clause += f"description @{match_index}@ $description_matches[0]"
            for match in description_matches[1:]:
                where_clause += f" OR description @{match_index}@ $description_matches[{match_index}]"
                match_index += 1
            where_clause += ")"
            params["description_matches"] = description_matches


        surql_query = """
        SELECT description,custodian_type.custodian_type AS custodian_type,assets_under_management,in.{name,identifier},out.{name,identifier} FROM custodian_for
        """
        
        if where_clause:
            surql_query += f"""
                WHERE {where_clause}
            """
        if order_by:
            surql_query += f"""
                ORDER BY {order_by}
            """
        if limit:
            surql_query += f"""
                LIMIT {limit}
            """
        

        graph_data = await self.connection.query(
           surql_query,params=params
        )
        return graph_data

        
    async def get_sma_graph(self):
        return self.get_custodian_graph(custodian_type = "SMA")
    

    async def get_cloud_graph(self):
        return self.get_custodian_graph(custodian_type = "A third-party unaffiliated record keeper",description_matches = ["cloud","data"])

        
    async def get_people(self):
       
        people = await self.connection.query(
            """  
            SELECT 
                first_name,
                last_name,
                full_name ,
                title,
                firm.{identifier,name},
                ->is_compliance_officer.{as_of_latest_filing_date,title_at_time_of_filing} as is_compliance_officer
                FROM person;
                """
        )
        return people
    

    async def get_filings(self):
       
        filings = await self.connection.query(
            """  
            SELECT 
            filing_id,  
            execution_type.execution_type AS execution_type,
            firm.{name,identifier},
            signatory.{full_name,title},
            <-signed.execution_date[0] AS execution_date 
            FROM filing;"""
        )
        return filings

    async def get_firms(self):
       
        firms = await self.connection.query(
            """
                   SELECT identifier,
                    legal_name,
                    name,
                    firm_type.firm_type AS firm_type,
                    city,
                    state,
                    country,
                    city,
                    postal_code,
                    chief_compliance_officer.full_name AS chief_compliance_officer
                    FROM firm;"""
        )
        return firms
        
    async def get_firm(self,firm_id):
        """
        Creates a new chat session in the database.

        Returns:
            dict: A dictionary containing the 'id' and 'title' of the newly created chat.
        """
        firm = await self.connection.query(
            """                                 
                
                SELECT 
                *,
                <-custodian_for.* AS firm_custodians,
                ->custodian_for.* AS firm_custodian_of,
                ->filed->filing<-signed AS firm_filings
                FROM type::thing("firm",$firm_id)
                FETCH chief_compliance_officer,
                    firm_type,
                    firm_custodians.in,
                    firm_custodians.in.firm_type,
                    firm_custodians.custodian_type,
                    firm_custodian_of.out,
                    firm_custodian_of.out.firm_type,
                    firm_custodian_of.custodian_type,
                    firm_filings,
                    firm_filings.in,
                    firm_filings.out;
                    
            """,
            params={"firm_id": firm_id}
        )
        return firm[0]
        
    async def get_person(self,firm_id,full_name):
        """
        Creates a new chat session in the database.

        Returns:
            dict: A dictionary containing the 'id' and 'title' of the newly created chat.
        """
        person = await self.connection.query(
            """                                 
                
                            
                SELECT 
                    *,
                ->signed AS signed_filings,
                ->is_compliance_officer AS compliance_officer_for
                    FROM type::thing("person",[$full_name,type::thing("firm",$firm_id)])

                FETCH firm, signed_filings,compliance_officer_for,signed_filings.out,signed_filings.out.execution_type;
                    
            """,
            params={"firm_id": firm_id,"full_name": full_name}
        )
        return person[0]
        
    async def get_filing(self,filing_id):
        """
        Creates a new chat session in the database.

        Returns:
            dict: A dictionary containing the 'id' and 'title' of the newly created chat.
        """
        filing = await self.connection.query(
            """                                 
                                
                SELECT *,<-filed AS filed,<-signed AS signed FROM type::thing("filing",$filing_id)
                FETCH firm,signatory,execution_type,filed,signed;
                                    
            """,
            params={"filing_id": filing_id}
        )
        return filing[0]
        