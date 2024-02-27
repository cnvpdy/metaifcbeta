import streamlit as st
from tools import ifchelper
import json
import ifcopenshell
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#################################### PDY #####################################
def calculate_wall_areas():
    walls = session.ifc_file.by_type("IfcWall")
    total_area = 0
    for wall in walls:
        for relation in wall.IsDefinedBy:
            if relation.RelatingPropertyDefinition.is_a("IfcElementQuantity"):
                quantities = relation.RelatingPropertyDefinition.Quantities
                for quantity in quantities:
                    if quantity.Name == "NetSideArea":
                        total_area += quantity.AreaValue
            elif relation.RelatingPropertyDefinition.is_a("IfcPropertySet"):
                for property in relation.RelatingPropertyDefinition.HasProperties:
                    if property.Name == "NetSideArea":
                        # 여기서 property 값을 올바르게 처리
                        # 예: total_area += property.NominalValue.wrappedValue 또는 적절한 속성 접근 방법 사용
                        pass
    return total_area
def calculate_wall_lengths():
    walls = session.ifc_file.by_type("IfcWall")
    total_length = 0
    for wall in walls:
        for relation in wall.IsDefinedBy:
            if relation.RelatingPropertyDefinition.is_a("IfcElementQuantity"):
                quantities = relation.RelatingPropertyDefinition.Quantities
                for quantity in quantities:
                    # Length 값을 찾을 때의 조건을 확인합니다.
                    if quantity.is_a("IfcQuantityLength") and quantity.Name == "Length":
                        total_length += quantity.LengthValue
            elif relation.RelatingPropertyDefinition.is_a("IfcPropertySet"):
                for property in relation.RelatingPropertyDefinition.HasProperties:
                    # 여기서 길이 관련 속성을 확인하고 처리합니다.
                    # 속성 이름이 Length가 아니라 다른 것일 수 있으니, IFC 파일을 확인해야 합니다.
                    if property.Name == "Length":
                        # 속성의 값 처리 방법은 속성의 타입에 따라 달라질 수 있습니다.
                        pass
    return total_length

def calculate_slab_perimeters():
    slabs = session.ifc_file.by_type("IfcSlab")
    total_perimeter = 0
    for slab in slabs:
        for relation in slab.IsDefinedBy:
            if relation.RelatingPropertyDefinition.is_a("IfcElementQuantity"):
                quantities = relation.RelatingPropertyDefinition.Quantities
                for quantity in quantities:
                    # Perimeter 값을 찾을 때의 조건을 확인합니다.
                    if quantity.is_a("IfcQuantityLength") and quantity.Name == "Perimeter":
                        total_perimeter += quantity.LengthValue
            elif relation.RelatingPropertyDefinition.is_a("IfcPropertySet"):
                for property in relation.RelatingPropertyDefinition.HasProperties:
                    # 여기서 둘레 관련 속성을 확인하고 처리합니다.
                    # 속성 이름이 Perimeter가 아니라 다른 것일 수 있으니, IFC 파일을 확인해야 합니다.
                    if property.Name == "Perimeter":
                        # 속성의 값 처리 방법은 속성의 타입에 따라 달라질 수 있습니다.
                        # 예: total_perimeter += property.NominalValue.wrappedValue
                        pass
    return total_perimeter

def calculate_gross_areas():
    elements = session.ifc_file.by_type("IfcSlab")  # 다른 요소 타입으로 변경 가능, 예: IfcWall, IfcFloor 등
    total_gross_area = 0
    for element in elements:
        for relation in element.IsDefinedBy:
            if relation.RelatingPropertyDefinition.is_a("IfcElementQuantity"):
                quantities = relation.RelatingPropertyDefinition.Quantities
                for quantity in quantities:
                    # GrossArea 값을 찾을 때의 조건을 확인합니다.
                    if quantity.is_a("IfcQuantityArea") and quantity.Name == "GrossArea":
                        total_gross_area += quantity.AreaValue
            elif relation.RelatingPropertyDefinition.is_a("IfcPropertySet"):
                for property in relation.RelatingPropertyDefinition.HasProperties:
                    # 여기서 면적 관련 속성을 확인하고 처리합니다.
                    # 속성 이름이 GrossArea가 아니라 다른 것일 수 있으니, IFC 파일을 확인해야 합니다.
                    if property.Name == "GrossArea":
                        # 속성의 값 처리 방법은 속성의 타입에 따라 달라질 수 있습니다.
                        # 예: total_gross_area += property.NominalValue.wrappedValue
                        pass
    return total_gross_area



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
    st.sidebar.success("Visualiser loaded")

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
        st.subheader("🧮 객체 속성 값")
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
            
def execute():
    initialise_debug_props()
    st.title("공사비 예측결과 요약") 
    if "ifc_file" in session and session["ifc_file"]:
        if "ifc_js_response" not in session:
            session["ifc_js_response"] = ""

        df_result_cost = pd.DataFrame({
            '총 공사비': ['벽 면적 합계' ],
            '건축 공사비': [f"㎡"],
            '토목 공사비': [f"㎡"],
            '조경 공사비': [f"㎡"],
            '기계 공사비': [f"㎡"],
            '전기 공사비': [f"㎡"],

        })
        st.dataframe(df_result_cost, use_container_width=True, hide_index = True)
        st.markdown(
            """
            ---

            """
        )

        col1, col2 = st.columns([2,1])
        with col1:
            draw_3d_viewer()
        with col2:

            tab1, tab2, tab3 = st.tabs(["공사비예측을 위한 수량","🧮 객체별 속성", "🩺 디버깅"])
            with tab1:
                #벽 수량
                st.header("벽")
                total_wall_area = calculate_wall_areas()
                total_wall_length= calculate_wall_lengths()


                dimensions_df = pd.DataFrame({
                    '항목': ['벽 면적 합계', '벽 길이 합계', ],
                    '값': [f"{total_wall_area}㎡", f"{total_wall_length}m"]
                })
                st.dataframe(dimensions_df, use_container_width=True, hide_index = True)
                #바닥
                st.header("바닥")
                total_slab_area = calculate_gross_areas()
                total_slab_perimeter = calculate_slab_perimeters()


                dimensions_df = pd.DataFrame({
                    '항목': ['바닥 면적 합계', '바닥 둘레 합계', ],
                    '값': [f"{total_slab_area}㎡", f"{total_slab_perimeter}m"]
                })
                st.dataframe(dimensions_df, use_container_width=True, hide_index = True)





            with tab2:
                write_pset_data()
            with tab3:
                write_health_data()
        with col1:
            tab1, tab2, tab3 = st.tabs(["총공사비","건축공사비", "토목공사비"])
            with tab1:
                tab1_, tab2_ = st.tabs(["안쪽","다시안쪽"])
                with tab1_:
                    # 샘플 데이터 생성
                    data = pd.DataFrame({
                        'x': np.random.randn(100),
                        'y': np.random.randn(100)
                    })
                    st.scatter_chart(data)
                with tab2_:
                    # 샘플 데이터 생성
                    data = pd.DataFrame({
                        'x': np.random.randn(100),
                        'y': np.random.randn(100)
                    })
                    st.scatter_chart(data)                 

  





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