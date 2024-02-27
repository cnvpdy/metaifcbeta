import streamlit as st
from tools import ifchelper
import json
import ifcopenshell
from tools import pandashelper
from tools import graph_maker



##################### STREAMLIT IFC-JS COMPONENT MAGIC ######################
from pathlib import Path                                                    #
from re import L                                                            #
from typing import Optional                                                 #
import streamlit.components.v1 as components                                #
#                                                                           #
#                                                                           #
# Tell streamlit that there is a component called ifc_js_viewer,            #
# and that the code to display that component is in the "frontend" folder   #
frontend_dir = (Path(__file__).parent / "frontend-viewer").absolute()       #
_component_func = components.declare_component(                             #
	"ifc_js_viewer", path=str(frontend_dir)                                 #
)                                                                           #
#                                                                           #
# Create the python function that will be called                            #
def ifc_js_viewer(                                                          #    
    url: Optional[str] = None,                                              #
):                                                                          #
    component_value = _component_func(                                      #
        url=url,                                                            #
    )                                                                       #
    return component_value                                                  #
#                                                                           #
#############################################################################

def draw_3d_viewer():
    def get_current_ifc_file():
        return session.array_buffer
    session.ifc_js_response = ifc_js_viewer(get_current_ifc_file())
    st.sidebar.success("3D뷰어 로드 성공")

def get_psets_from_ifc_js():
    if session.ifc_js_response:
        return json.loads(session.ifc_js_response)
        
def format_ifc_js_psets(data):
    return ifchelper.format_ifcjs_psets(data)


def initialise_debug_props(force=False):
    if not "BIMDebugProperties" in session:
        session.BIMDebugProperties = {
            "step_id": 0,
            "number_of_polygons": 0,
            "percentile_of_polygons": 0,
            "active_step_id": 0,
            "step_id_breadcrumb": [],
            "attributes": [],
            "inverse_attributes": [],
            "inverse_references": [],
            "express_file": None,
        }
    if force:
        session.BIMDebugProperties = {
            "step_id": 0,
            "number_of_polygons": 0,
            "percentile_of_polygons": 0,
            "active_step_id": 0,
            "step_id_breadcrumb": [],
            "attributes": [],
            "inverse_attributes": [],
            "inverse_references": [],
            "express_file": None,
        }

def get_object_data(fromId=None):
    def add_attribute(prop, key, value):
        if isinstance(value, tuple) and len(value) < 10:
            for i, item in enumerate(value):
                add_attribute(prop, key + f"[{i}]", item)
            return
        elif isinstance(value, tuple) and len(value) >= 10:
            key = key + "({})".format(len(value))
        
        propy = {
            "name": key,
            "string_value": str(value),
            "int_value": int(value.id()) if isinstance(value, ifcopenshell.entity_instance) else None,
        }
        prop.append(propy)
            
    if session.BIMDebugProperties:
        initialise_debug_props(force=True)
        step_id = 0
        if fromId:
            step_id =  int(fromId)
        else:
            step_id = int(session.object_id) if session.object_id else 0
        debug_props = st.session_state.BIMDebugProperties
        debug_props["active_step_id"] = step_id
        
        crumb = {"name": str(step_id)}
        debug_props["step_id_breadcrumb"].append(crumb)
        element = session.ifc_file.by_id(step_id)
        debug_props["inverse_attributes"] = []
        debug_props["inverse_references"] = []
        
        if element:
        
            for key, value in element.get_info().items():
                add_attribute(debug_props["attributes"], key, value)

            for key in dir(element):
                if (
                    not key[0].isalpha()
                    or key[0] != key[0].upper()
                    or key in element.get_info()
                    or not getattr(element, key)
                ):
                    continue
                add_attribute(debug_props["inverse_attributes"], key, getattr(element, key))
            
            for inverse in session.ifc_file.get_inverse(element):
                propy = {
                    "string_value": str(inverse),
                    "int_value": inverse.id(),
                }
                debug_props["inverse_references"].append(propy)
                
            print(debug_props["attributes"])

def edit_object_data(object_id, attribute):
    entity = session.ifc_file.by_id(object_id)
    print(getattr(entity, attribute))
    
def write_pset_data():
    data = get_psets_from_ifc_js()
    if data:
        st.subheader("🧮 Object Properties")
        psets = format_ifc_js_psets(data['props'])
        for pset in psets.values():
            st.subheader(pset["Name"])
            st.table(pset["Data"])    

def write_health_data():
    st.subheader("🩺 Debugger")
    ## REPLICATE IFC DEBUG PANNEL
    row1_col1, row1_col2 = st.columns([1,5])
    with row1_col1:
        st.number_input("Object ID", key="object_id")
    with row1_col2:
        st.button("Inspect From Id", key="edit_object_button", on_click=get_object_data, args=(st.session_state.object_id,))
        data = get_psets_from_ifc_js()
        if data:
            st.button("Inspect from Model", key="get_object_button", on_click=get_object_data, args=(data['id'],)) if data else ""

    if "BIMDebugProperties" in session and session.BIMDebugProperties:
        props = session.BIMDebugProperties
        if props["attributes"]:
            st.subheader("Attributes")
            # st.table(props["attributes"])
            for prop in props["attributes"]:
                col2, col3 = st.columns([3,3])
                if prop["int_value"]:
                    col2.text(f'🔗 {prop["name"]}')
                    col2.info(prop["string_value"])
                    col3.write("🔗")
                    col3.button("Get Object", key=f'get_object_pop_button_{prop["int_value"]}', on_click=get_object_data, args=(prop["int_value"],))
                else:
                    col2.text_input(label=prop["name"], key=prop["name"], value=prop["string_value"])
                    # col3.button("Edit Object", key=f'edit_object_{prop["name"]}', on_click=edit_object_data, args=(props["active_step_id"],prop["name"]))
                    
        if props["inverse_attributes"]:
            st.subheader("Inverse Attributes")
            for inverse in props["inverse_attributes"]:
                col1, col2, col3 = st.columns([3,5,8])
                col1.text(inverse["name"])
                col2.text(inverse["string_value"])
                if inverse["int_value"]:
                    col3.button("Get Object", key=f'get_object_pop_button_{inverse["int_value"]}', on_click=get_object_data, args=(inverse["int_value"],))
        
        ## draw inverse references
        if props["inverse_references"]:
            st.subheader("Inverse References")
            for inverse in props["inverse_references"]:
                col1, col3 = st.columns([3,3])
                col1.text(inverse["string_value"])
                if inverse["int_value"]:
                    col3.button("Get Object", key=f'get_object_pop_button_inverse_{inverse["int_value"]}', on_click=get_object_data, args=(inverse["int_value"],))

def initialize_session_state():
    session["DataFrame"] = None
    session["Classes"] = []
    session["IsDataFrameLoaded"] = False

def load_data():
    if "ifc_file" in session:
        session["DataFrame"] = get_ifc_pandas()
        session.Classes = session.DataFrame["Class"].value_counts().keys().tolist()
        session["IsDataFrameLoaded"] = True

def get_ifc_pandas():
    data, pset_attributes = ifchelper.get_objects_data_by_class(
        session.ifc_file, 
        "IfcBuildingElement"
    )
    frame = ifchelper.create_pandas_dataframe(data, pset_attributes)
    return frame

def download_csv():
    pandashelper.download_csv(session.file_name,session.DataFrame)

def download_excel():
    pandashelper.download_excel(session.file_name,session.DataFrame)




def execute():
    initialise_debug_props()
    st.title("공사비 예측결과 상세") 
    if "ifc_file" in session and session["ifc_file"]:
        if "ifc_js_response" not in session:
            session["ifc_js_response"] = ""
            st.header("3D뷰어")
        draw_3d_viewer()
        if not "IsDataFrameLoaded" in session:
            initialize_session_state()
        if not session.IsDataFrameLoaded:
            load_data()
        if session.IsDataFrameLoaded:    
            tab1, tab2 = st.tabs(["Dataframe Utilities", "Quantities Review"])
            with tab1:
                ## DATAFRAME REVIEW            
                st.header("DataFrame Review")  
                st.write(session.DataFrame)
                # from st_aggrid import AgGrid
                # AgGrid(session.DataFrame)
                st.button("Download CSV", key="download_csv", on_click=download_csv)
                st.button("Download Excel", key="download_excel", on_click=download_excel)
            with tab2:
                row2col1, row2col2 = st.columns(2)
                with row2col1:
                    if session.IsDataFrameLoaded:
                        class_selector = st.selectbox("Select Class", session.Classes, key="class_selector")
                        session["filtered_frame"] = pandashelper.filter_dataframe_per_class(session.DataFrame, session.class_selector)
                        session["qtos"] = pandashelper.get_qsets_columns(session["filtered_frame"])
                        if session["qtos"] is not None:
                            qto_selector = st.selectbox("Select Quantity Set", session.qtos, key='qto_selector')
                            quantities = pandashelper.get_quantities(session.filtered_frame, session.qto_selector)
                            st.selectbox("Select Quantity", quantities, key="quantity_selector")
                            st.radio('Split per', ['Level', 'Type'], key="split_options")
                        else:
                            st.warning("No Quantities to Look at !")
                ## DRAW FRAME
                with row2col2: 
                    if "quantity_selector" in session and session.quantity_selector == "Count":
                        total = pandashelper.get_total(session.filtered_frame)
                        st.write(f"The total number of {session.class_selector} is {total}")
                    else:
                        if session.qtos is not None:
                            st.subheader(f"{session.class_selector} {session.quantity_selector}")
                            graph = graph_maker.load_graph(
                                session.filtered_frame,
                                session.qto_selector,
                                session.quantity_selector,
                                session.split_options,                                
                            )
                            st.plotly_chart(graph)

    else:
        st.markdown(
            """
            ---
            #### 👈 '홈' 메뉴를 누르고 사이드바에서 IFC파일을 로드하세요.
            ---
            """
        )




session = st.session_state
execute()