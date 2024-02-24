import streamlit as st
import ifcopenshell

def callback_upload():
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

def get_project_name():
    return session.ifc_file.by_type("IfcProject")[0].Name

def change_project_name():
    if session.project_name_input:
        session.ifc_file.by_type("IfcProject")[0].Name = session.project_name_input
        

def main():
         
    st.set_page_config(
        layout= "wide",
        page_title="IFC 견적",
        page_icon="🏢",
         
    )
    st.title("BIM기반 개산견적 시스템") 

    
    ## Add File uploader to Side Bar Navigation
    st.sidebar.header('IFC 로드')
    st.sidebar.file_uploader("파일 선택", type=['ifc'], key="uploaded_file", on_change=callback_upload,)
    
    if "is_file_loaded" in session and session["is_file_loaded"]:
        st.sidebar.success(f"프로젝트가 로드되었습니다.")
        st.sidebar.write("새 파일로 다시 로드할 수 있습니다.")
        col1, col2 = st.columns([2,1])
        col1.subheader(f'프로젝트명 : "{get_project_name()}"')
        col2.text_input("✏️프로젝트명 변경", key="project_name_input")
        col2.button("✔️ 변경", key="change_project_name", on_click=change_project_name())
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