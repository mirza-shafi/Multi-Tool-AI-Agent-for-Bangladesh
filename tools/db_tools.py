"""Text-to-SQL tools over the 3 Bangladesh SQLite databases.

Each tool is a self-contained pipeline: natural-language question -> LLM
writes a SELECT against the known schema -> execute on that dataset's
SQLite file -> LLM turns the raw rows into a natural-language answer.
"""

import os
import re

from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import Tool

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db")

SQL_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a SQLite expert. Given the table schema below, write a single "
            "read-only SQLite SELECT query that answers the user's question. "
            "Use LIKE with wildcards for fuzzy text matching (e.g. city/cuisine names). "
            "Return ONLY the raw SQL query - no explanation, no markdown code fences.\n\n"
            "Schema:\n{schema}",
        ),
        ("human", "{question}"),
    ]
)

ANSWER_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant. Given the user's question and the SQL "
            "query result below, answer in clear natural language. If the result "
            "is empty, say plainly that no matching records were found. Do not "
            "mention SQL or the query itself in your answer.",
        ),
        ("human", "Question: {question}\nSQL query: {sql}\nResult: {result}"),
    ]
)


def _clean_sql(raw_sql: str) -> str:
    cleaned = raw_sql.strip()
    cleaned = re.sub(r"^```(sql)?", "", cleaned, flags=re.IGNORECASE).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()
    return cleaned.rstrip(";")


def make_db_tool(name: str, description: str, db_filename: str, table_name: str, llm):
    db_path = os.path.join(DB_DIR, db_filename)
    db = SQLDatabase.from_uri(f"sqlite:///{db_path}", include_tables=[table_name])
    schema = db.get_table_info()

    sql_chain = SQL_PROMPT | llm
    answer_chain = ANSWER_PROMPT | llm

    def _run(question: str) -> str:
        sql = _clean_sql(sql_chain.invoke({"schema": schema, "question": question}).content)

        if not sql.lower().startswith("select"):
            return "I could only generate a non-SELECT query for that question, which isn't allowed. Please rephrase."

        try:
            result = db.run(sql)
        except Exception as exc:
            return f"The query failed to run: {exc}"

        return answer_chain.invoke({"question": question, "sql": sql, "result": result}).content

    return Tool(name=name, description=description, func=_run)


def get_institutions_tool(llm) -> Tool:
    return make_db_tool(
        name="InstitutionsDBTool",
        description=(
            "Use for questions about Bangladeshi educational institutions - schools, "
            "colleges, madrasahs (universities are not covered by this dataset). "
            "Table columns: institute_name, eiin, institute_type, division, district, "
            "thana, union_name, mauza_name, area_status, geographical_status, address, "
            "post, management_type (govt/non-govt), mobile, student_type, "
            "education_level, affiliation, mpo_status. Input should be a plain-English "
            "question, e.g. 'How many government institutions are in Rajshahi?'"
        ),
        db_filename="institutions.db",
        table_name="institutions",
        llm=llm,
    )


def get_hospitals_tool(llm) -> Tool:
    return make_db_tool(
        name="HospitalsDBTool",
        description=(
            "Use for questions about Bangladeshi health facilities under DGHS - "
            "hospitals, health complexes, health offices. Table columns: id, name, "
            "name_bangla, code, agency, facility_type, division, district, "
            "city_corporation, upazila, paurasava, union_name, is_private (0/1). "
            "Note: this dataset does NOT contain bed counts or doctor counts. "
            "Input should be a plain-English question, e.g. 'How many hospitals are "
            "in Dhaka?'"
        ),
        db_filename="hospitals.db",
        table_name="hospitals",
        llm=llm,
    )


def get_restaurants_tool(llm) -> Tool:
    return make_db_tool(
        name="RestaurantsDBTool",
        description=(
            "Use for questions about Bangladeshi restaurants - ratings, reviews, "
            "location. Table columns: place_id, name, latitude, longitude, rating, "
            "number_of_reviews, affluence, address. Note: there is no explicit "
            "cuisine or city column, so location/cuisine questions are matched "
            "against the name/address text. Input should be a plain-English "
            "question, e.g. 'Find restaurants in Chattogram serving biryani.'"
        ),
        db_filename="restaurants.db",
        table_name="restaurants",
        llm=llm,
    )
