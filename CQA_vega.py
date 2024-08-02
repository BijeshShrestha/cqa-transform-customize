import os
from dotenv import load_dotenv
import datetime
import altair as alt
import pandas as pd

# Import classes related to the agent setup
from llama_index.llms.openai import OpenAI
from llama_index.core.agent import ReActAgent, FunctionCallingAgentWorker, AgentRunner

# Import classes for chat messages and tools
from llama_index.core.llms import ChatMessage
from llama_index.core.tools import BaseTool, FunctionTool, QueryEngineTool, ToolMetadata

# Import classes for data indexing and storage
from llama_index.core import VectorStoreIndex, StorageContext, SimpleDirectoryReader, load_index_from_storage
from llama_index.core.objects import ObjectIndex

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Define the Vega-Lite bar chart creation tool using Altair
def create_vega_bar_chart(data, title="Bar Chart", x_label="X-axis", y_label="Y-axis", color="skyblue"):
    if isinstance(data, list) and all(isinstance(item, list) for item in data):
        data = {item[0]: item[1] for item in data}
    elif not isinstance(data, dict):
        raise ValueError("Data must be a dictionary or a list of lists.")

    df = pd.DataFrame(list(data.items()), columns=[x_label, y_label])

    chart = alt.Chart(df).mark_bar(color=color).encode(
        x=alt.X(x_label, sort=None),
        y=y_label
    ).properties(
        title=title
    )

    directory = "temp_img"
    if not os.path.exists(directory):
        os.makedirs(directory)
    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{directory}/{title.replace(' ', '_')}_{current_time}.html"
    chart.save(filename)
    print(f"Saved chart as {filename}")

# Define the Vega-Lite line chart creation tool using Altair
def create_vega_line_chart(data, title="Line Chart", x_label="X-axis", y_label="Y-axis", color="skyblue"):
    if isinstance(data, list) and all(isinstance(item, list) for item in data):
        data = {item[0]: item[1] for item in data}
    elif not isinstance(data, dict):
        raise ValueError("Data must be a dictionary or a list of lists.")

    df = pd.DataFrame(list(data.items()), columns=[x_label, y_label])

    chart = alt.Chart(df).mark_line(color=color).encode(
        x=alt.X(x_label, sort=None),
        y=y_label
    ).properties(
        title=title
    )

    directory = "temp_img"
    if not os.path.exists(directory):
        os.makedirs(directory)
    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{directory}/{title.replace(' ', '_')}_{current_time}.html"
    chart.save(filename)
    print(f"Saved chart as {filename}")

# Define the bar chart creation tool
bar_chart_tool = FunctionTool.from_defaults(
    fn=create_vega_bar_chart,
    name="vega_bar_chart_creator",
    description="Generates a dynamic Vega-Lite bar chart based on provided data and parameters."
)

# Define the line chart creation tool
line_chart_tool = FunctionTool.from_defaults(
    fn=create_vega_line_chart,
    name="vega_line_chart_creator",
    description="Generates a dynamic Vega-Lite line chart based on provided data and parameters."
)

try:
    storage_context = StorageContext.from_defaults(
        persist_dir="./test_files/textdata"
    )
    text_index = load_index_from_storage(storage_context)

    storage_context = StorageContext.from_defaults(
        persist_dir="./test_files/chartdata"
    )
    chart_index = load_index_from_storage(storage_context)

    index_loaded = True
except:
    index_loaded = False

if not index_loaded:
    text_docs = SimpleDirectoryReader(
        input_files=["./test_files/inflation2024_report.pdf"]
    ).load_data()
    chart_docs = SimpleDirectoryReader(
        input_files=["./test_files/inflation2024_data_chart.pdf"]
    ).load_data()

    text_index = VectorStoreIndex.from_documents(text_docs)
    chart_index = VectorStoreIndex.from_documents(chart_docs)

    text_index.storage_context.persist(persist_dir="./test_files/textdata")
    chart_index.storage_context.persist(persist_dir="./test_files/chartdata")

text_engine = text_index.as_query_engine(similarity_top_k=3)
chart_engine = chart_index.as_query_engine(similarity_top_k=3)

query_engine_tools = [
    QueryEngineTool(
        query_engine=text_engine,
        metadata=ToolMetadata(
            name="textdata",
            description=(
                "Provides information about text in the document. "
                "Use a detailed plain text question as input to the tool."
            ),
        ),
    ),
    QueryEngineTool(
        query_engine=chart_engine,
        metadata=ToolMetadata(
            name="chartdata",
            description=(
                "Provides information about chart data in the document."
                "Use a detailed plain text question as input to the tool."
            ),
        ),
    ),
    bar_chart_tool,
    line_chart_tool,
]

obj_index = ObjectIndex.from_objects(
    query_engine_tools,
    index_cls=VectorStoreIndex,
)

llm = OpenAI(model="gpt-3.5-turbo")
agent_worker = FunctionCallingAgentWorker.from_tools(
    tool_retriever=obj_index.as_retriever(similarity_top_k=5),
    llm=llm,
    verbose=True,
    allow_parallel_tool_calls=True,
)
agent = AgentRunner(agent_worker)

def process_inquiry_and_show_latest_image(question):
    inquiry_time = datetime.datetime.now()
    response = agent.chat(question)
    
    print(f"{response}")

    directory = 'temp_img'
    latest_file = None
    latest_time = inquiry_time

    if os.path.exists(directory):
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                file_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                if file_time > latest_time:
                    latest_time = file_time
                    latest_file = file_path

    if latest_file:
        return latest_file
    return None
