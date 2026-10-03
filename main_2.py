from nicegui import ui, app
import pandas as pd
import plotly.express as px
import asyncio  
# NAYA IMPORT: delete_dataset add kar diya gaya hai
from db_handler import init_db, create_user, verify_user, process_and_store_universal_data, get_user_datasets, load_dataset_from_db, delete_dataset
from brain import chat_with_data

init_db()

def logout():
    app.storage.user.clear()
    ui.navigate.to('/login')

def apply_native_theme():
    """Sets Quasar's Native Colors."""
    ui.colors(
        primary='#2563eb',    
        secondary='#10b981',  
        accent='#f59e0b',     
        positive='#22c55e',   
        negative='#ef4444'    
    )

# --- AUTHENTICATION PAGE ---
@ui.page('/login')
def login_page():
    if app.storage.user.get('authenticated', False):
        ui.navigate.to('/')
        return

    apply_native_theme()
    ui.dark_mode().value = False

    with ui.column().classes('w-full min-h-screen items-center justify-center'):
        with ui.card().classes('w-full max-w-md shadow-2xl p-8 rounded-xl'):
            with ui.row().classes('w-full justify-center items-center gap-2 mb-2'):
                ui.icon('auto_graph', size='xl').classes('text-primary') 
                ui.label('FinSecure AI').classes('text-4xl font-extrabold tracking-tight')

            ui.label('Data Intelligence Engine').classes('w-full text-center opacity-50 mb-8 font-medium')
            
            username = ui.input('Username').classes('w-full mb-4').props('outlined rounded')
            password = ui.input('Password', password=True, password_toggle_button=True).classes('w-full mb-8').props('outlined rounded')
            
            def try_login():
                if verify_user(username.value, password.value):
                    app.storage.user['authenticated'] = True
                    app.storage.user['username'] = username.value
                    ui.notify('Welcome to Dashboard!', color='positive', icon='check_circle')
                    ui.navigate.to('/')
                else:
                    ui.notify('Invalid Credentials', color='negative', icon='error')

            def try_register():
                if create_user(username.value, password.value):
                    ui.notify('Account Created! Please Login.', color='positive', icon='done_all')
                else:
                    ui.notify('Username exists!', color='warning', icon='warning')

            ui.button('Sign In', on_click=try_login, icon='login').classes('w-full mb-4 py-3 text-lg font-bold shadow-md').props('rounded unelevated color="primary"')
            ui.button('Create New Account', on_click=try_register).classes('w-full py-2 text-lg font-bold').props('flat rounded color="secondary"')


# --- MAIN DASHBOARD ---
@ui.page('/')
def dashboard():
    if not app.storage.user.get('authenticated', False):
        ui.navigate.to('/login')
        return

    current_user = app.storage.user['username']
    if 'active_table' not in app.storage.user:
        app.storage.user['active_table'] = None

    apply_native_theme()
    dark = ui.dark_mode()

    with ui.header(elevated=True).classes('justify-between items-center bg-primary text-white p-4'):
        with ui.row().classes('items-center gap-3'):
            ui.icon('hub', size='md')
            ui.label('FinSecure AI').classes('text-2xl font-black tracking-wide')

        with ui.row().classes('items-center gap-6'):
            ui.switch('Dark Mode').bind_value(dark, 'value').props('color="accent"')
            ui.label(f'👤 {current_user}').classes('font-bold text-lg border-l border-white/30 pl-6')
            ui.button('Logout', on_click=logout, icon='logout').classes('py-1 px-4 font-bold shadow-sm').props('rounded color="negative"')

    with ui.column().classes('w-full max-w-7xl mx-auto mt-8 p-4'):
        
        with ui.tabs().classes('w-full justify-evenly border-b border-gray-200 dark:border-gray-800') as tabs:
            tab_db = ui.tab('Data Catalog', icon='dns').classes('text-sm font-bold tracking-wide')
            tab_upload = ui.tab('ETL Pipeline', icon='route').classes('text-sm font-bold tracking-wide')
            tab_eda = ui.tab('Data Profiling', icon='troubleshoot').classes('text-sm font-bold tracking-wide')
            tab_visual = ui.tab('Studio', icon='space_dashboard').classes('text-sm font-bold tracking-wide')
            tab_ai = ui.tab('AI Agent', icon='memory').classes('text-sm font-bold tracking-wide')

        with ui.tab_panels(tabs, value=tab_db).classes('w-full mt-6 bg-transparent'):
            
            # --- TAB 1: DATABASE MANAGER (WITH DELETE FEATURE) ---
            with ui.tab_panel(tab_db):
                with ui.card().classes('w-full p-8 shadow-lg rounded-xl'):
                    ui.label('Data Catalog Registry').classes('text-3xl font-extrabold mb-6')
                    
                    # NAYA: Auto-Refreshable Data Catalog Component
                    @ui.refreshable
                    def render_catalog():
                        datasets_df = get_user_datasets(current_user)
                        
                        if datasets_df.empty:
                            ui.label('Registry is empty. Go to ETL Pipeline to ingest data.').classes('text-xl opacity-50')
                        else:
                            options = {row['table_name']: f"{row['original_filename']} ({row['row_count']} rows)" for _, row in datasets_df.iterrows()}
                            
                            with ui.row().classes('w-full items-center gap-4 mb-8'):
                                dataset_selector = ui.select(options=options, label='Select Active Dataset').classes('w-1/2 flex-grow').props('outlined rounded')
                                if app.storage.user['active_table'] in options:
                                    dataset_selector.value = app.storage.user['active_table']
                                
                                def select_dataset(e):
                                    app.storage.user['active_table'] = e.value
                                    ui.notify(f"Activated: {e.value}", color='positive', icon='dataset')
                                dataset_selector.on_value_change(select_dataset)
                                
                                # DELETE FUNCTIONALITY LOGIC
                                def delete_selected():
                                    tbl = dataset_selector.value
                                    if tbl:
                                        success, msg = delete_dataset(current_user, tbl)
                                        if success:
                                            ui.notify(msg, color='positive', icon='delete_forever')
                                            # Agar active data delete hua toh system se reset karo
                                            if app.storage.user.get('active_table') == tbl:
                                                app.storage.user['active_table'] = None
                                            render_catalog.refresh() # UI automatically update hogi
                                        else:
                                            ui.notify(msg, color='negative', icon='error')
                                            
                                ui.button('Delete Dataset', on_click=delete_selected, icon='delete').classes('h-14 px-8 font-bold shadow-md').props('rounded unelevated color="negative"')
                            
                            cols = [{'name': c, 'label': c.title().replace('_', ' '), 'field': c} for c in datasets_df.columns]
                            ui.table(columns=cols, rows=datasets_df.to_dict('records')).classes('w-full shadow-md rounded-lg')
                    
                    render_catalog()

            # --- TAB 2: UNIVERSAL UPLOAD ---
            with ui.tab_panel(tab_upload):
                with ui.card().classes('w-full p-8 shadow-lg rounded-xl items-center'):
                    ui.icon('cloud_upload', size='6rem').classes('text-primary opacity-80 mb-4')
                    ui.label('Data Ingestion Engine').classes('text-3xl font-extrabold mb-2')
                    ui.label('Drop your .csv, .xlsx, .json, or .arff files here').classes('text-xl opacity-50 mb-8')
                    
                    async def handle_upload(e):
                        with ui.dialog() as loading_dialog, ui.card().classes('items-center p-10 rounded-xl shadow-2xl'):
                            ui.spinner('cube', size='4xl', color='primary').classes('mb-6')
                            ui.label('Parsing Data & Building Schema...').classes('text-2xl font-black mb-2')
                            ui.label('Please wait. Large files take a few seconds.').classes('opacity-50 text-lg')
                        
                        loading_dialog.open()
                        await asyncio.sleep(0.1) 
                        
                        try:
                            file_obj = e.file if hasattr(e, 'file') else e.content
                            file_bytes = await file_obj.read()
                            file_name = getattr(e, 'name', getattr(file_obj, 'name', getattr(file_obj, 'filename', 'data.csv')))
                            
                            success, msg = process_and_store_universal_data(file_bytes, file_name, current_user)
                            
                            if success:
                                datasets = get_user_datasets(current_user)
                                if not datasets.empty:
                                    app.storage.user['active_table'] = datasets.iloc[0]['table_name']
                                ui.notify(msg, color='positive', icon='verified')
                                render_catalog.refresh() # NAYA: Upload hote hi list auto-update hogi
                                tabs.set_value(tab_eda)
                            else:
                                ui.notify(msg, color='negative', icon='error')
                        except Exception as ex:
                            ui.notify(f"System Error: {str(ex)}", color='negative')
                        finally:
                            loading_dialog.close() 
                            
                    ui.upload(on_upload=handle_upload, auto_upload=True).classes('w-full max-w-lg border-2 border-dashed border-primary rounded-xl p-8')

            # --- TAB 3: EXPLORATORY DATA ANALYSIS ---
            with ui.tab_panel(tab_eda):
                with ui.card().classes('w-full p-8 shadow-lg rounded-xl'):
                    active_tbl = app.storage.user.get('active_table')
                    if not active_tbl:
                        ui.label('⚠️ No active dataset. Select one in Data Catalog.').classes('text-negative text-2xl font-bold')
                    else:
                        df = load_dataset_from_db(active_tbl)
                        ui.label(f'Data Profiling: {active_tbl}').classes('text-3xl font-extrabold mb-8')
                        
                        with ui.row().classes('w-full grid grid-cols-1 md:grid-cols-2 gap-6 mb-8'):
                            with ui.card().classes('items-center p-6 shadow-md border-t-4 border-primary'):
                                ui.icon('storage', size='lg').classes('text-primary mb-2')
                                ui.label('TOTAL RECORDS').classes('font-bold opacity-50 tracking-widest')
                                ui.label(f'{df.shape[0]:,}').classes('text-5xl font-black text-primary mt-2')
                            
                            with ui.card().classes('items-center p-6 shadow-md border-t-4 border-secondary'):
                                ui.icon('view_column', size='lg').classes('text-secondary mb-2')
                                ui.label('TOTAL FEATURES').classes('font-bold opacity-50 tracking-widest')
                                ui.label(f'{df.shape[1]}').classes('text-5xl font-black text-secondary mt-2')
                        
                        ui.label('📈 Statistical Distribution (Numeric Features)').classes('text-2xl font-bold mb-4')
                        try:
                            numeric_df = df.select_dtypes(include=['number'])
                            if not numeric_df.empty:
                                stats_df = numeric_df.describe().reset_index().round(2).astype(str)
                                stats_df.rename(columns={'index': 'Metric'}, inplace=True)
                                stats_cols = [{'name': col, 'label': col.title(), 'field': col} for col in stats_df.columns]
                                ui.table(columns=stats_cols, rows=stats_df.to_dict('records')).classes('w-full shadow-md rounded-lg mb-8')
                            else:
                                ui.label('No numerical features found for statistical analysis.').classes('text-lg opacity-50 mb-8 italic')
                        except Exception as e:
                            ui.label(f'Could not generate statistics: {str(e)}').classes('text-negative mb-8')

                        ui.label('Live Data Preview (Top 10 Rows)').classes('text-2xl font-bold mb-4')
                        preview_df = df.head(10).fillna('NaN').astype(str)
                        cols = [{'name': col, 'label': col.title(), 'field': col} for col in preview_df.columns]
                        ui.table(columns=cols, rows=preview_df.to_dict('records')).classes('w-full shadow-md rounded-lg')

            # --- TAB 4: DYNAMIC VISUALIZATIONS ---
            with ui.tab_panel(tab_visual):
                with ui.card().classes('w-full p-8 shadow-lg rounded-xl'):
                    active_tbl = app.storage.user.get('active_table')
                    if not active_tbl:
                        ui.label('⚠️️ No active dataset. Select one in Data Catalog.').classes('text-negative text-2xl font-bold')
                    else:
                        df = load_dataset_from_db(active_tbl)
                        ui.label('Visualization Studio').classes('text-3xl font-extrabold mb-6')
                        
                        with ui.row().classes('w-full grid grid-cols-1 md:grid-cols-4 gap-4 items-center mb-8'):
                            col_list = list(df.columns)
                            x_axis = ui.select(options=col_list, label='X-Axis', value=col_list[0] if len(col_list) > 0 else '').classes('w-full').props('outlined rounded')
                            y_axis = ui.select(options=col_list, label='Y-Axis', value=col_list[-1] if len(col_list) > 0 else '').classes('w-full').props('outlined rounded')
                            chart_type = ui.select(options=['Bar Chart', 'Scatter Plot', 'Line Chart', 'Area Chart'], label='Chart Type', value='Bar Chart').classes('w-full').props('outlined rounded')
                            ui.button('Render Chart', on_click=lambda: generate_chart(), icon='play_arrow').classes('w-full h-14 font-bold text-lg shadow-md').props('rounded unelevated color="primary"')
                            
                        chart_container = ui.column().classes('w-full h-[500px] border rounded-xl overflow-hidden shadow-inner p-2')

                        def generate_chart():
                            chart_container.clear()
                            try:
                                with chart_container:
                                    template = 'plotly_dark' if dark.value else 'plotly_white'
                                    if chart_type.value == 'Bar Chart':
                                        fig = px.bar(df, x=x_axis.value, y=y_axis.value, template=template, color_discrete_sequence=['#2563eb'])
                                    elif chart_type.value == 'Scatter Plot':
                                        fig = px.scatter(df, x=x_axis.value, y=y_axis.value, template=template, color_discrete_sequence=['#10b981'])
                                    elif chart_type.value == 'Line Chart':
                                        fig = px.line(df, x=x_axis.value, y=y_axis.value, template=template, color_discrete_sequence=['#f59e0b'])
                                    elif chart_type.value == 'Area Chart':
                                        fig = px.area(df, x=x_axis.value, y=y_axis.value, template=template, color_discrete_sequence=['#22c55e'])
                                    
                                    fig.update_layout(margin=dict(l=40, r=40, t=40, b=40), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                                    ui.plotly(fig).classes('w-full h-full')
                            except Exception as ex:
                                with chart_container:
                                    ui.label(f'Plot Error: Variables may not be compatible. ({str(ex)})').classes('text-negative font-bold text-xl p-8')
                        
                        dark.on_value_change(generate_chart)
                        generate_chart()

            # --- TAB 5: AI CHAT ---
            with ui.tab_panel(tab_ai):
                with ui.card().classes('w-full p-8 shadow-lg rounded-xl'):
                    active_tbl = app.storage.user.get('active_table')
                    if not active_tbl:
                        ui.label('⚠️ No active dataset. Select one in Data Catalog.').classes('text-negative text-2xl font-bold')
                    else:
                        with ui.row().classes('items-center gap-3 mb-6'):
                            ui.icon('smart_toy', size='xl').classes('text-primary')
                            ui.label(f'AI Copilot (Dataset: {active_tbl})').classes('text-3xl font-extrabold')
                        
                        chat_container = ui.column().classes('w-full h-[450px] overflow-y-auto p-4 rounded-xl border shadow-inner')
                        
                        with chat_container:
                            ui.chat_message('Hello! Ask me any question about your data.', name='AI Engine', stamp='System', avatar='https://cdn-icons-png.flaticon.com/512/4712/4712035.png')

                        def send_message():
                            user_text = chat_input.value
                            if not user_text: return
                            
                            with chat_container:
                                ui.chat_message(user_text, name=current_user, sent=True, avatar='https://cdn-icons-png.flaticon.com/512/3135/3135715.png')
                            
                            chat_input.value = ''
                            df = load_dataset_from_db(active_tbl)
                            try:
                                reply = chat_with_data(df, user_text) 
                            except Exception as ex:
                                reply = f"Error processing query: {str(ex)}"
                                
                            with chat_container:
                                ui.chat_message(reply, name='AI Engine', stamp='System', avatar='https://cdn-icons-png.flaticon.com/512/4712/4712035.png')
                                
                        with ui.row().classes('w-full mt-6 items-center gap-4'):
                            chat_input = ui.input('Type your data query here...').classes('flex-grow').props('outlined rounded')
                            ui.button('Ask', on_click=send_message, icon='send').classes('h-14 px-8 shadow-md text-lg font-bold').props('rounded unelevated color="primary"')

ui.run(title='FinSecure AI - Intelligent Dashboard', storage_secret='minor_project_secret', port=8080)