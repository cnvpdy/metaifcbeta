import streamlit as st
import ifcopenshell
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import altair as alt

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

def calculate_slab_grossAreas():
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
def calculate_window_quantities():
    windows = session.ifc_file.by_type("IfcWindow")
    window_count = len(windows)  # ifcWindow 객체의 개수
    total_perimeter = 0
    total_area = 0
    
    for window in windows:
        for relation in window.IsDefinedBy:
            if relation.RelatingPropertyDefinition.is_a("IfcElementQuantity"):
                quantities = relation.RelatingPropertyDefinition.Quantities
                for quantity in quantities:
                    # Perimeter 값 추출
                    if quantity.Name == "Perimeter":
                        total_perimeter += quantity.LengthValue
                    # Area 값 추출
                    elif quantity.Name == "Area":
                        total_area += quantity.AreaValue
    
    return window_count, total_perimeter, total_area

def format_number(number):
    # 숫자를 반올림하여 정수로 변환
    rounded_number = round(number)
    # 천 단위마다 콤마를 찍어서 포맷
    formatted_number = "{:,}".format(rounded_number)
    return formatted_number

#------------------------------------------------------------------------------------------------------------------

def callback_upload():
    if session["uploaded_file"]:
        session["file_name"] = session["uploaded_file"].name
        session["array_buffer"] = session["uploaded_file"].getvalue()
        session["ifc_file"] = ifcopenshell.file.from_string(session["array_buffer"].decode("utf-8"))
        session["is_file_loaded"] = True
        
        ### Empty Previous Model Data from Session State
        session["isHealthDataLoaded"] = False
        session["HealthData"] = {}
        session["Graphs"] = {}
        session["SequenceData"] = {}
        session["CostScheduleData"] = {}

        ### Empty Previous DataFrame from Session State
        session["DataFrame"] = None
        session["Classes"] = []
        session["IsDataFrameLoaded"] = False
        
        ## ifc_file에 데이터가 있을 경우 실행
        if "is_file_loaded" in session and session["is_file_loaded"]:
            session["total_wall_area"] = calculate_wall_areas()
            session["total_wall_length"] = calculate_wall_lengths()/1000
            session["total_slab_area"] = calculate_slab_grossAreas()
            session["total_slab_perimeter"] = calculate_slab_perimeters()/1000
            session["total_window_count"] = calculate_window_quantities()[0]
            session["total_window_perimeter"] = calculate_window_quantities()[1]
            session["total_window_area"] = calculate_window_quantities()[2]
            session["total_cost"] = session["total_slab_area"]*1500000


def get_project_name():
    return session.ifc_file.by_type("IfcProject")[0].Name

def change_project_name():
    if session.project_name_input:
        session.ifc_file.by_type("IfcProject")[0].Name = session.project_name_input
def draw_3d_viewer():
    def get_current_ifc_file():
        return session.array_buffer
    session.ifc_js_response = ifc_js_viewer(get_current_ifc_file())
    st.sidebar.success("Visualiser loaded")

def main():
         
    st.set_page_config(
        layout= "wide",
        page_title="IFC 견적",
        page_icon="🏢",
         
    )


    
    ## Add File uploader to Side Bar Navigation
    st.sidebar.header('IFC 로드')
    st.sidebar.file_uploader("파일 선택", type=['ifc'], key="uploaded_file", on_change=callback_upload,)
    
    if "is_file_loaded" in session and session["is_file_loaded"]:
        
        total_cost = format_number(session["total_cost"])
        
        st.markdown("---")
        st.markdown(f"##### 총 공사비 : {total_cost}원")
        st.markdown("---")


        col1, col2 = st.columns([2,1])
        with col1:
            draw_3d_viewer()
        with col2:

            tab1, tab2 = st.tabs(["수량 집계","-"])
            with tab1:
                tab_wall, tab_slab, tab_window = st.tabs(["벽","바닥","창문"])
                with tab_wall:
                    #벽 수량
                    print(session["total_wall_area"])
                    total_wall_area = session["total_wall_area"]
                    total_wall_length= session["total_wall_length"]


                    dimensions_df = pd.DataFrame({
                        '항목': ['벽 면적 합계', '벽 길이 합계', ],
                        '값': [f"{total_wall_area}㎡", f"{total_wall_length}m"]
                    })
                    st.dataframe(dimensions_df,  hide_index = True)
                    st.markdown("---")
                with tab_slab:
                    #바닥

                    total_slab_area = session["total_slab_area"]
                    total_slab_perimeter = session["total_slab_perimeter"]


                    dimensions_df = pd.DataFrame({
                        '항목': ['바닥 면적 합계', '바닥 둘레 합계', ],
                        '값': [f"{total_slab_area}㎡", f"{total_slab_perimeter}m"]
                    })
                    st.dataframe(dimensions_df,  hide_index = True)

                with tab_window:
                    #창문

                    total_window_count = session["total_window_count"]
                    total_window_area = session["total_window_area"]
                    total_window_perimeter = session["total_window_perimeter"]

                    dimensions_df = pd.DataFrame({
                        '항목': ['창문 개수', '창문 면적 합계','창문 둘레 합계' ],
                        '값': [f"{total_window_count}ea", f"{total_window_area}m2", f"{total_window_perimeter}m"]
                    })
                    st.dataframe(dimensions_df,  hide_index = True)







            with tab2:
                st.write('')

        st.markdown("""
                    ---
                    ### 학습 데이터 분석
                    """)

        tab1_, tab2_,tab3_,tab4_,tab5_,tab6_,tab7_= st.tabs(["[벽 면적 합계]","[벽 길이 합계]","[바닥 면적 합계]","[바닥 둘레 합계]","[창문 개수]","[창문 둘레 합계]","[창문 면적 합계]"])
        with tab1_:

            data = pd.DataFrame({
                'x': np.random.randn(100),
                'y': np.random.randn(100)
            })

            # 강조할 조건 추가 (예: x 값이 양수 중 최대값)
            data['highlight'] = data['x'] == data[data['x'] > 0]['x'].max()

            # 산점도 그리기
            chart = alt.Chart(data).mark_circle(size=60).encode(
                x='x',
                y='y',
                color=alt.condition(
                    alt.datum.highlight,  # 조건
                    alt.value('red'),     # 조건이 참일 때 색상
                    alt.value('blue')     # 조건이 거짓일 때 색상
                )
            ).interactive()  # 상호작용 가능하게 만들기
            st.altair_chart(chart, use_container_width=True)
        with tab2_:
            data = pd.DataFrame({
                'x': np.random.randn(100),
                'y': np.random.randn(100)
            })

            # 강조할 조건 추가 (예: x 값이 양수 중 최대값)
            data['highlight'] = data['x'] == data[data['x'] > 0]['x'].max()

            # 산점도 그리기
            chart = alt.Chart(data).mark_circle(size=60).encode(
                x='x',
                y='y',
                color=alt.condition(
                    alt.datum.highlight,  # 조건
                    alt.value('red'),     # 조건이 참일 때 색상
                    alt.value('blue')     # 조건이 거짓일 때 색상
                )
            ).interactive()  # 상호작용 가능하게 만들기     
            st.altair_chart(chart, use_container_width=True)
        with tab3_:
            data = pd.DataFrame({
                'x': np.random.randn(100),
                'y': np.random.randn(100)
            })

            # 강조할 조건 추가 (예: x 값이 양수 중 최대값)
            data['highlight'] = data['x'] == data[data['x'] > 0]['x'].max()

            # 산점도 그리기
            chart = alt.Chart(data).mark_circle(size=60).encode(
                x='x',
                y='y',
                color=alt.condition(
                    alt.datum.highlight,  # 조건
                    alt.value('red'),     # 조건이 참일 때 색상
                    alt.value('blue')     # 조건이 거짓일 때 색상
                )
            ).interactive()  # 상호작용 가능하게 만들기
            st.altair_chart(chart, use_container_width=True)   
        with tab4_:
            data = pd.DataFrame({
                'x': np.random.randn(100),
                'y': np.random.randn(100)
            })

            # 강조할 조건 추가 (예: x 값이 양수 중 최대값)
            data['highlight'] = data['x'] == data[data['x'] > 0]['x'].max()

            # 산점도 그리기
            chart = alt.Chart(data).mark_circle(size=60).encode(
                x='x',
                y='y',
                color=alt.condition(
                    alt.datum.highlight,  # 조건
                    alt.value('red'),     # 조건이 참일 때 색상
                    alt.value('blue')     # 조건이 거짓일 때 색상
                )
            ).interactive()  # 상호작용 가능하게 만들기   
            st.altair_chart(chart, use_container_width=True)
        with tab5_:
            data = pd.DataFrame({
                'x': np.random.randn(100),
                'y': np.random.randn(100)
            })

            # 강조할 조건 추가 (예: x 값이 양수 중 최대값)
            data['highlight'] = data['x'] == data[data['x'] > 0]['x'].max()

            # 산점도 그리기
            chart = alt.Chart(data).mark_circle(size=60).encode(
                x='x',
                y='y',
                color=alt.condition(
                    alt.datum.highlight,  # 조건
                    alt.value('red'),     # 조건이 참일 때 색상
                    alt.value('blue')     # 조건이 거짓일 때 색상
                )
            ).interactive()  # 상호작용 가능하게 만들기   
            st.altair_chart(chart, use_container_width=True)
        with tab6_:
            data = pd.DataFrame({
                'x': np.random.randn(100),
                'y': np.random.randn(100)
            })

            # 강조할 조건 추가 (예: x 값이 양수 중 최대값)
            data['highlight'] = data['x'] == data[data['x'] > 0]['x'].max()

            # 산점도 그리기
            chart = alt.Chart(data).mark_circle(size=60).encode(
                x='x',
                y='y',
                color=alt.condition(
                    alt.datum.highlight,  # 조건
                    alt.value('red'),     # 조건이 참일 때 색상
                    alt.value('blue')     # 조건이 거짓일 때 색상
                )
            ).interactive()  # 상호작용 가능하게 만들기   
            st.altair_chart(chart, use_container_width=True)
        with tab7_:
            data = pd.DataFrame({
                'x': np.random.randn(100),
                'y': np.random.randn(100)
            })

            # 강조할 조건 추가 (예: x 값이 양수 중 최대값)
            data['highlight'] = data['x'] == data[data['x'] > 0]['x'].max()

            # 산점도 그리기
            chart = alt.Chart(data).mark_circle(size=60).encode(
                x='x',
                y='y',
                color=alt.condition(
                    alt.datum.highlight,  # 조건
                    alt.value('red'),     # 조건이 참일 때 색상
                    alt.value('blue')     # 조건이 거짓일 때 색상
                )
            ).interactive()  # 상호작용 가능하게 만들기   
            st.altair_chart(chart, use_container_width=True)





    else:
        st.markdown(
            """
            ---
            #### 👈 사이드바에서 IFC파일을 로드하세요.
            ---
            """
        )

if __name__ == "__main__":
    session = st.session_state
    main()