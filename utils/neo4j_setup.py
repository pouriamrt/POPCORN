import neo4j
from neo4j_graphrag.llm import OpenAILLM as LLM
from neo4j_graphrag.embeddings.openai import OpenAIEmbeddings as Embeddings
from neo4j_graphrag.generation.graphrag import GraphRAG
from neo4j_graphrag.generation import RagTemplate
from neo4j_graphrag.retrievers import HybridCypherRetriever
import os

def setup_neo4j_and_llm():
    driver = neo4j.GraphDatabase.driver(
        os.getenv("NEO4J_URI"),
        auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
    )
    embedder = Embeddings()
    llm = LLM(model_name="gpt-4o", model_params={"temperature": 0.0})

    retrieval_query = """
    WITH node AS chunk
    MATCH (chunk)<-[:FROM_CHUNK]-()-[rel*1..2]-()
    OPTIONAL MATCH ()-[rel0]-()-[:HAS_ABSTRACT]->(chunk)
    UNWIND rel AS single_rel
    UNWIND rel0 AS single_rel0
    WITH [c IN collect(DISTINCT chunk) WHERE c IS NOT NULL] AS chunks,
         [r IN collect(DISTINCT single_rel) WHERE r IS NOT NULL] AS rels,
         [r0 IN collect(DISTINCT single_rel0) WHERE r0 IS NOT NULL] AS rels0
    WITH chunks[0..$top_k] AS limited_chunks, rels, rels0
    RETURN '=== kg_rels (incoming) ===\\n' + 
           apoc.text.join([r0 IN rels0 | coalesce(startNode(r0).name, startNode(r0).title, '') + ' - ' + type(r0) + '(' + coalesce(r0.details, '') + ')' + ' -> ' + coalesce(endNode(r0).name, endNode(r0).title, '')], '\\n---\\n ********* \\n---\\n') +
           '\\n\\n=== text ===\\n' + 
           apoc.text.join([c IN limited_chunks | c.text], '\\n---\\n') +
           '\\n\\n=== kg_rels (outgoing) ===\\n' +
           apoc.text.join([r IN rels | coalesce(startNode(r).name, startNode(r).title, '') + ' - ' + type(r) + '(' + coalesce(r.details, '') + ')' + ' -> ' + coalesce(endNode(r).name, endNode(r).title, '')], '\\n---\\n ********* \\n---\\n') AS info
    """

    retriever = HybridCypherRetriever(
        driver=driver,
        vector_index_name="text_embeddings",
        fulltext_index_name="paper_fulltext_index",
        retrieval_query=retrieval_query,
        embedder=embedder
    )

    template = RagTemplate(
        template='''Answer the Question using the following Context. Only respond with information mentioned in the Context. Do not inject speculative information.\n\n# Question:\n{query_text}\n\n# Context:\n{context}\n\n# Answer:\n''',
        expected_inputs=['query_text', 'context']
    )

    return GraphRAG(llm=llm, retriever=retriever, prompt_template=template)
