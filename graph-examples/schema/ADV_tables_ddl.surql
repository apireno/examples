/*
This file defines the SurrealQL for the chat functionality of this project. and functions that span either embedding model
*/

DEFINE ANALYZER IF NOT EXISTS snowball_analyzer
    TOKENIZERS class
    FILTERS lowercase, snowball(english);



DEFINE TABLE IF NOT EXISTS firm_type SCHEMAFULL;
DEFINE FIELD IF NOT EXISTS firm_type ON TABLE firm_type TYPE string;
UPSERT firm_type:`ERA` CONTENT{
    firm_type : 'ERA'};
UPSERT firm_type:`Registered` CONTENT{
    firm_type : 'Registered'};
UPSERT firm_type:`Records Holder` CONTENT{
    firm_type : 'Records Holder'};



DEFINE TABLE IF NOT EXISTS firm SCHEMAFULL;
DEFINE FIELD IF NOT EXISTS name ON TABLE firm TYPE string;
DEFINE FIELD IF NOT EXISTS identifier ON TABLE firm TYPE string;
DEFINE FIELD IF NOT EXISTS firm_type ON TABLE firm TYPE Record<firm_type>;
DEFINE FIELD IF NOT EXISTS legal_name ON TABLE firm TYPE Option<string>;
DEFINE FIELD IF NOT EXISTS city ON TABLE firm TYPE Option<string>;
DEFINE FIELD IF NOT EXISTS state ON TABLE firm TYPE Option<string>;
DEFINE FIELD IF NOT EXISTS country ON TABLE firm TYPE Option<string>;

-- Define fields for section1
DEFINE FIELD IF NOT EXISTS section1 ON TABLE firm TYPE Option<object>;
DEFINE FIELD IF NOT EXISTS section1.sec_region ON TABLE firm TYPE Option<string>;
DEFINE FIELD IF NOT EXISTS section1.organization_crd ON TABLE firm TYPE Option<int>;
DEFINE FIELD IF NOT EXISTS section1.firm_type ON TABLE firm TYPE Option<string>;
DEFINE FIELD IF NOT EXISTS section1.cik ON TABLE firm TYPE Option<int>;
DEFINE FIELD IF NOT EXISTS section1.primary_business_name ON TABLE firm TYPE Option<string>;
DEFINE FIELD IF NOT EXISTS section1.legal_name ON TABLE firm TYPE Option<string>;
DEFINE FIELD IF NOT EXISTS section1.main_office_street_address_1 ON TABLE firm TYPE Option<string>;
DEFINE FIELD IF NOT EXISTS section1.main_office_street_address_2 ON TABLE firm TYPE Option<string>;
DEFINE FIELD IF NOT EXISTS section1.main_office_city ON TABLE firm TYPE Option<string>;
DEFINE FIELD IF NOT EXISTS section1.main_office_state ON TABLE firm TYPE Option<string>;
DEFINE FIELD IF NOT EXISTS section1.main_office_country ON TABLE firm TYPE Option<string>;
DEFINE FIELD IF NOT EXISTS section1.main_office_postal_code ON TABLE firm TYPE Option<string>;
DEFINE FIELD IF NOT EXISTS section1.chief_compliance_officer_name ON TABLE firm TYPE Option<string>;
DEFINE FIELD IF NOT EXISTS section1.chief_compliance_officer_other_titles ON TABLE firm TYPE Option<string>;
DEFINE FIELD IF NOT EXISTS section1.latest_adv_filing_date ON TABLE firm TYPE Option<datetime>;
DEFINE FIELD IF NOT EXISTS section1.website_address ON TABLE firm TYPE Option<string>;
-- Define fields for section_5d
DEFINE FIELD IF NOT EXISTS section_5d ON TABLE firm TYPE Option<object>;
DEFINE FIELD IF NOT EXISTS section_5d.approx_amount_of_assets ON TABLE firm TYPE Option<string>;
DEFINE FIELD IF NOT EXISTS section_5d.individuals_other_than_high_net_worth_number_of_clients ON TABLE firm TYPE Option<int>;
DEFINE FIELD IF NOT EXISTS section_5d.individuals_other_than_high_net_worth_regulatory_assets ON TABLE firm TYPE Option<decimal>;
DEFINE FIELD IF NOT EXISTS section_5d.high_net_worth_individuals_number_of_clients ON TABLE firm TYPE Option<int>;
DEFINE FIELD IF NOT EXISTS section_5d.high_net_worth_individuals_regulatory_assets ON TABLE firm TYPE Option<decimal>;
DEFINE FIELD IF NOT EXISTS section_5d.banking_or_thrift_institutions_number_of_clients ON TABLE firm TYPE Option<int>;
DEFINE FIELD IF NOT EXISTS section_5d.banking_or_thrift_institutions_regulatory_assets ON TABLE firm TYPE Option<decimal>;
DEFINE FIELD IF NOT EXISTS section_5d.investment_companies_number_of_clients ON TABLE firm TYPE Option<int>;
DEFINE FIELD IF NOT EXISTS section_5d.investment_companies_regulatory_assets ON TABLE firm TYPE Option<decimal>;
DEFINE FIELD IF NOT EXISTS section_5d.business_development_companies_number_of_clients ON TABLE firm TYPE Option<int>;
DEFINE FIELD IF NOT EXISTS section_5d.business_development_companies_regulatory_assets ON TABLE firm TYPE Option<decimal>;
DEFINE FIELD IF NOT EXISTS section_5d.pooled_investment_vehicles_number_of_clients ON TABLE firm TYPE Option<int>;
DEFINE FIELD IF NOT EXISTS section_5d.pooled_investment_vehicles_regulatory_assets ON TABLE firm TYPE Option<decimal>;
DEFINE FIELD IF NOT EXISTS section_5d.pension_and_profit_sharing_plans_number_of_clients ON TABLE firm TYPE Option<int>;
DEFINE FIELD IF NOT EXISTS section_5d.pension_and_profit_sharing_plans_regulatory_assets ON TABLE firm TYPE Option<decimal>;
DEFINE FIELD IF NOT EXISTS section_5d.charitable_organizations_number_of_clients ON TABLE firm TYPE Option<int>;
DEFINE FIELD IF NOT EXISTS section_5d.charitable_organizations_regulatory_assets ON TABLE firm TYPE Option<decimal>;
DEFINE FIELD IF NOT EXISTS section_5d.state_or_municipal_government_entities_number_of_clients ON TABLE firm TYPE Option<int>;
DEFINE FIELD IF NOT EXISTS section_5d.state_or_municipal_government_entities_regulatory_assets ON TABLE firm TYPE Option<decimal>;
DEFINE FIELD IF NOT EXISTS section_5d.other_investment_advisers_number_of_clients ON TABLE firm TYPE Option<int>;
DEFINE FIELD IF NOT EXISTS section_5d.other_investment_advisers_regulatory_assets ON TABLE firm TYPE Option<decimal>;
DEFINE FIELD IF NOT EXISTS section_5d.insurance_companies_number_of_clients ON TABLE firm TYPE Option<int>;
DEFINE FIELD IF NOT EXISTS section_5d.insurance_companies_regulatory_assets ON TABLE firm TYPE Option<decimal>;
DEFINE FIELD IF NOT EXISTS section_5d.sovereign_wealth_funds_number_of_clients ON TABLE firm TYPE Option<int>;
DEFINE FIELD IF NOT EXISTS section_5d.sovereign_wealth_funds_regulatory_assets ON TABLE firm TYPE Option<decimal>;
DEFINE FIELD IF NOT EXISTS section_5d.corporations_or_other_businesses_number_of_clients ON TABLE firm TYPE Option<int>;
DEFINE FIELD IF NOT EXISTS section_5d.corporations_or_other_businesses_regulatory_assets ON TABLE firm TYPE Option<decimal>;
DEFINE FIELD IF NOT EXISTS section_5d.other_number_of_clients ON TABLE firm TYPE Option<int>;
DEFINE FIELD IF NOT EXISTS section_5d.other_regulatory_assets ON TABLE firm TYPE Option<decimal>;
DEFINE FIELD IF NOT EXISTS section_5d.other_details ON TABLE firm TYPE Option<string>;

-- Define fields for section_5f
DEFINE FIELD IF NOT EXISTS section_5f ON TABLE firm TYPE object;
DEFINE FIELD IF NOT EXISTS section_5f.discretionary_regulatory_assets ON TABLE firm TYPE Option<decimal>;
DEFINE FIELD IF NOT EXISTS section_5f.nondiscretionary_regulatory_assets ON TABLE firm TYPE Option<decimal>;
DEFINE FIELD IF NOT EXISTS section_5f.total_regulatory_assets ON TABLE firm TYPE Option<decimal>;
DEFINE FIELD IF NOT EXISTS section_5f.discretionary_accounts ON TABLE firm TYPE Option<int>;
DEFINE FIELD IF NOT EXISTS section_5f.nondiscretionary_accounts ON TABLE firm TYPE Option<int>;
DEFINE FIELD IF NOT EXISTS section_5f.total_accounts ON TABLE firm TYPE Option<int>;
DEFINE FIELD IF NOT EXISTS section_5f.nonus_regulatory_assets ON TABLE firm TYPE Option<decimal>;

DEFINE INDEX IF NOT EXISTS name_text_index ON TABLE firm
    FIELDS name SEARCH ANALYZER snowball_analyzer BM25;

DEFINE INDEX IF NOT EXISTS identifier_index ON firm
    FIELDS identifier;

DEFINE INDEX IF NOT EXISTS cik_index ON firm
    FIELDS section1.cik;

DEFINE INDEX IF NOT EXISTS firm_type_index ON firm
    FIELDS firm_type.firm_type;




DEFINE TABLE IF NOT EXISTS sma TYPE RELATION
IN firm OUT firm SCHEMAFULL;
DEFINE FIELD IF NOT EXISTS source_filing ON TABLE sma TYPE Record<filing>;
DEFINE FIELD IF NOT EXISTS legal_entity_identifier ON TABLE sma TYPE Option<string>;
DEFINE FIELD IF NOT EXISTS assets_under_management ON TABLE sma TYPE Option<decimal>;
DEFINE FIELD IF NOT EXISTS related_person ON TABLE sma TYPE bool;



DEFINE TABLE IF NOT EXISTS filing SCHEMAFULL;
DEFINE FIELD IF NOT EXISTS filing_id ON TABLE filing TYPE int;
DEFINE FIELD IF NOT EXISTS filing_firm ON TABLE filing TYPE Record<firm>;
DEFINE FIELD IF NOT EXISTS execution_type ON TABLE filing TYPE Record<ia_filing_execution_type>;
DEFINE FIELD IF NOT EXISTS execution_date ON TABLE filing TYPE datetime;
DEFINE FIELD IF NOT EXISTS signatory ON TABLE filing TYPE Record<person>;
DEFINE FIELD IF NOT EXISTS signitory_title ON TABLE filing TYPE string;


DEFINE TABLE IF NOT EXISTS ia_filing_execution_type SCHEMAFULL;
DEFINE FIELD IF NOT EXISTS execution_type ON TABLE ia_filing_execution_type TYPE string;



DEFINE TABLE IF NOT EXISTS person SCHEMAFULL;
DEFINE FIELD IF NOT EXISTS full_name ON TABLE person TYPE string;
DEFINE FIELD IF NOT EXISTS first_name ON TABLE person TYPE Option<string>;
DEFINE FIELD IF NOT EXISTS last_name ON TABLE person TYPE Option<string>;
DEFINE FIELD IF NOT EXISTS title ON TABLE person TYPE Option<string>;

