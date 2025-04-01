

class SurrealDML():
    """
    This class contains SurrealQL Data Manipulation Language (DML) queries.

    These queries are used to interact with the SurrealDB database for data insertion,
    retrieval, and manipulation.
    """
    


    def DELETE_CORPUS_TABLE_INFO(TABLE_NAME:str):
        """
        SurrealQL query to delete a corpus table info record and its associated model information.

        Args:
            TABLE_NAME (str): The name of the corpus table to delete.

        Returns:
            str: The SurrealQL query string.
        """
        return f"""
                DELETE FROM corpus_table_model WHERE corpus_table = corpus_table:{TABLE_NAME};
                DELETE corpus_table:{TABLE_NAME};  
            """
    
 
    def DELETE_CORPUS_GRAPH_TABLE_INFO(TABLE_NAME:str):
        """
        SurrealQL query to delete a corpus graph table info record.

        Args:
            TABLE_NAME (str): The name of the corpus graph table to delete.

        Returns:
            str: The SurrealQL query string.
        """
        return f"""
                DELETE corpus_graph_tables:{TABLE_NAME};  
            """
    

        
    def UPDATE_CORPUS_TABLE_INFO(TABLE_NAME:str,DISPLAY_NAME:str):
        """
        SurrealQL query to update or insert corpus table information.

        This query updates the table's metadata, including chunk size and associated embedding models.

        Args:
            TABLE_NAME (str): The name of the corpus table to update.
            DISPLAY_NAME (str): The display name of the corpus table.

        Returns:
            str: The SurrealQL query string.
        """
          
        return f"""

                LET $chunk_size =  IF $chunk_size = None THEN 
                    math::ceil(math::mean( SELECT VALUE text.split(' ').len() FROM embedded_wiki))
                ELSE 
                    $chunk_size
                END; 
                DELETE FROM corpus_table_model WHERE corpus_table = corpus_table:{TABLE_NAME};
                FOR $model IN $embed_models {{
                    LET $model_definition = type::thing("embedding_model_definition",$model.model_id);
                    UPSERT corpus_table_model:[corpus_table:{TABLE_NAME},$model_definition] SET model = $model_definition,field_name = $model.field_name, corpus_table=corpus_table:{TABLE_NAME};
                }};
                UPSERT corpus_table:{TABLE_NAME} SET table_name = '{TABLE_NAME}', display_name = '{DISPLAY_NAME}', chunk_size = $chunk_size,
                    embed_models = (SELECT value id FROM corpus_table_model WHERE corpus_table = corpus_table:{TABLE_NAME}) RETURN NONE;
                    
            """
    

        
    def UPDATE_CORPUS_GRAPH_TABLE_INFO(TABLE_NAME:str):
        """
        SurrealQL query to update or insert corpus graph table information.

        This query updates the table's metadata, including associated entity, relation,
        and source document table names.

        Args:
            TABLE_NAME (str): The name of the corpus graph table to update.

        Returns:
            str: The SurrealQL query string.
        """
        return f"""

                LET $display_name = 
                (SELECT VALUE display_name FROM corpus_table WHERE table_name = '{TABLE_NAME}')[0];

                UPSERT corpus_graph_tables:{TABLE_NAME} SET corpus_table = corpus_table:{TABLE_NAME}, 

                entity_display_name = $display_name + " Entities",
                entity_table_name = $entity_table_name,

                relation_display_name =  $display_name + " Relationships",
                relation_table_name = $relation_table_name,

                source_document_display_name = $display_name + " Documents",
                source_document_table_name = $source_document_table_name,

                relation_date_field = $relation_date_field,
                entity_date_field = $entity_date_field
                  RETURN NONE;
            """
    

    def INSERT_RECORDS(TABLE_NAME:str):

        """
        SurrealQL query to insert records into a corpus table.

        Args:
            TABLE_NAME (str): The name of the corpus table to insert into.

        Returns:
            str: The SurrealQL query string.
        """


        return f"""
        FOR $row IN $records {{
            CREATE type::thing("{TABLE_NAME}",$row.url)  CONTENT {{
                url : $row.url,
                title: $row.title,
                text: $row.text,
                content_glove_vector: IF $row.content_glove_vector= NULL THEN None ELSE $row.content_glove_vector END,
                content_openai_vector: IF $row.content_openai_vector= NULL THEN None ELSE $row.content_openai_vector END,
                content_fasttext_vector: IF $row.content_fasttext_vector= NULL THEN None ELSE $row.content_fasttext_vector END,
                additional_data: IF $row.additional_data= NULL THEN None ELSE $row.additional_data END
            }} RETURN NONE;
        }};
    """

    def UPSERT_RECORDS(TABLE_NAME:str):

        """
        SurrealQL query to upsert (insert or update) records in a corpus table.

        Args:
            TABLE_NAME (str): The name of the corpus table to upsert into.

        Returns:
            str: The SurrealQL query string.
        """

        return f"""
        FOR $row IN $records {{
            UPSERT type::thing("{TABLE_NAME}",$row.url)  CONTENT {{
                url : $row.url,
                title: $row.title,
                text: $row.text,
                content_glove_vector: IF $row.content_glove_vector= NULL THEN None ELSE $row.content_glove_vector END,
                content_openai_vector: IF $row.content_openai_vector= NULL THEN None ELSE $row.content_openai_vector END,
                content_fasttext_vector: IF $row.content_fasttext_vector= NULL THEN None ELSE $row.content_fasttext_vector END,
                additional_data: IF $row.additional_data= NULL THEN None ELSE $row.additional_data END
            }} RETURN NONE;
        }};
    """


    def UPSERT_SOURCE_DOCUMENTS(TABLE_NAME:str):
        """
        SurrealQL query to upsert records in a source document table.

        Args:
            TABLE_NAME (str): The name of the source document table to upsert into.

        Returns:
            str: The SurrealQL query string.
        """

        return f"""
        FOR $row IN $records {{
            UPSERT type::thing("{TABLE_NAME}",$row.url)  CONTENT {{
                url : $row.url,
                title: $row.title,
                additional_data: IF $row.additional_data= NULL THEN None ELSE $row.additional_data END
            }} RETURN NONE;
        }};
    """


    # SurrealQL query to insert corpus graph entity table records
    def INSERT_GRAPH_ENTITY_RECORDS(TABLE_NAME:str,SOURCE_DOCUMENT_TABLE_NAME:str):
        """
        SurrealQL query to insert records into a corpus graph entity table.

        Args:
            TABLE_NAME (str): The name of the entity table to insert into.
            SOURCE_DOCUMENT_TABLE_NAME (str): The name of the source document table.

        Returns:
            str: The SurrealQL query string.
        """

        return f"""
        FOR $row IN $records {{
            CREATE type::thing("{TABLE_NAME}",$row.full_id)  CONTENT {{
                source_document : type::thing("{SOURCE_DOCUMENT_TABLE_NAME}",$row.url),
                entity_type: $row.entity_type,
                identifier: $row.identifier,
                name: $row.name,
                contexts: $row.contexts,
                context_glove_vector: IF $row.content_glove_vector= NULL THEN None ELSE $row.content_glove_vector END,
                context_openai_vector: IF $row.content_openai_vector= NULL THEN None ELSE $row.content_openai_vector END,
                context_fasttext_vector: IF $row.content_fasttext_vector= NULL THEN None ELSE $row.content_fasttext_vector END,
                additional_data: IF $row.additional_data = NULL THEN None ELSE $row.additional_data END
            }} RETURN NONE;
        }};
    """


    # SurrealQL query to insert corpus graph entity table records
    def UPSERT_GRAPH_ENTITY_RECORDS(TABLE_NAME:str,SOURCE_DOCUMENT_TABLE_NAME:str):
        """
        SurrealQL query to upsert records in a corpus graph entity table.

        Args:
            TABLE_NAME (str): The name of the entity table to upsert into.
            SOURCE_DOCUMENT_TABLE_NAME (str): The name of the source document table.

        Returns:
            str: The SurrealQL query string.
        """

        return f"""
        FOR $row IN $records {{
            UPSERT type::thing("{TABLE_NAME}",$row.full_id)  CONTENT {{
                source_document : type::thing("{SOURCE_DOCUMENT_TABLE_NAME}",$row.url),
                entity_type: $row.entity_type,
                identifier: $row.identifier,
                name: $row.name,
                contexts: $row.contexts,
                context_glove_vector: IF $row.content_glove_vector= NULL THEN None ELSE $row.content_glove_vector END,
                context_openai_vector: IF $row.content_openai_vector= NULL THEN None ELSE $row.content_openai_vector END,
                context_fasttext_vector: IF $row.content_fasttext_vector= NULL THEN None ELSE $row.content_fasttext_vector END,
                additional_data: IF $row.additional_data = NULL THEN None ELSE $row.additional_data END
            }} RETURN NONE;
        }};
    """



    # SurrealQL query to insert corpus graph entity table records
    def INSERT_GRAPH_RELATION_RECORDS(ENTITY_TABLE_NAME:str,RELATE_TABLE_NAME:str,SOURCE_DOCUMENT_TABLE_NAME:str):

        """
        SurrealQL query to insert records into a corpus graph relation table.

        Args:
            ENTITY_TABLE_NAME (str): The name of the entity table.
            RELATE_TABLE_NAME (str): The name of the relation table.
            SOURCE_DOCUMENT_TABLE_NAME (str): The name of the source document table.

        Returns:
            str: The SurrealQL query string.
        """


        return f"""
        # entity1 and entity2 are arrays in format [source_document,entity_type,identifier] that are the ids
        FOR $row IN $records {{
            LET $ent1 = type::thing("{ENTITY_TABLE_NAME}",$row.entity1);
            LET $ent2 = type::thing("{ENTITY_TABLE_NAME}",$row.entity2);
            RELATE 
            $ent1
                -> {RELATE_TABLE_NAME} -> 
            $ent2
                  CONTENT {{
                source_document : type::thing("{SOURCE_DOCUMENT_TABLE_NAME}",$row.url),
                confidence: $row.confidence,
                relationship: $row.relationship,
                contexts: $row.contexts,
                context_glove_vector: IF $row.content_glove_vector= NULL THEN None ELSE $row.content_glove_vector END,
                context_openai_vector: IF $row.content_openai_vector= NULL THEN None ELSE $row.content_openai_vector END,
                context_fasttext_vector: IF $row.content_fasttext_vector= NULL THEN None ELSE $row.content_fasttext_vector END
            }} RETURN NONE;
        }};
    """


    # SurrealQL query to insert corpus graph entity table records
    def UPSERT_GRAPH_RELATION_RECORDS(ENTITY_TABLE_NAME:str,RELATE_TABLE_NAME:str,SOURCE_DOCUMENT_TABLE_NAME:str):

        """
        SurrealQL query to upsert records in a corpus graph relation table.

        Args:
            ENTITY_TABLE_NAME (str): The name of the entity table.
            RELATE_TABLE_NAME (str): The name of the relation table.
            SOURCE_DOCUMENT_TABLE_NAME (str): The name of the source document table.

        Returns:
            str: The SurrealQL query string.
        """


        return f"""
        # entity1 and entity2 are arrays in format [source_document,entity_type,identifier] that are the ids
        FOR $row IN $records {{
            LET $ent1 = type::thing("{ENTITY_TABLE_NAME}",$row.entity1);
            LET $ent2 = type::thing("{ENTITY_TABLE_NAME}",$row.entity2);
            RELATE 
            $ent1
                -> {RELATE_TABLE_NAME} -> 
            $ent2
                  CONTENT {{
                source_document : type::thing("{SOURCE_DOCUMENT_TABLE_NAME}",$row.url),
                confidence: $row.confidence,
                relationship: $row.relationship,
                contexts: $row.contexts,
                context_glove_vector: IF $row.content_glove_vector= NULL THEN None ELSE $row.content_glove_vector END,
                context_openai_vector: IF $row.content_openai_vector= NULL THEN None ELSE $row.content_openai_vector END,
                context_fasttext_vector: IF $row.content_fasttext_vector= NULL THEN None ELSE $row.content_fasttext_vector END
            }} RETURN NONE;
        }};
    """

