from analysis import *
from req_and_exp import *

st.title("Weather anomalies analysis")
st.badge("Applied Python HW 01", color="blue")

st.markdown("")
st.markdown("## Data upload & Setting Up Parameters")

submitted = None
global flag
flag = None

uploaded_file = st.file_uploader(
        label='Upload historical data',
        type=['csv'],
        help="Upload CSV file with **city, timestamp, temperature, season** cols"
    )

if uploaded_file is not None:
    form = st.form("my_form")
    data = pd.read_csv(uploaded_file)
    pos_cities_options = data.city.unique()
    exp_options = form.multiselect(
        "The types of parallel experiments",
        ["Sync", "Async", "Multithread"],
        default=["Sync", "Async", "Multithread"],
    )
    city_option = form.selectbox(
        "The city",
        pos_cities_options,
        help="Actually, you can choose the only one city. I just like design of mult thing"
    )
    API_key = form.text_input(
        label="Open Weather API key",
        value="",
        help="Your Open Weather API key"
    )
    submitted = form.form_submit_button("Start Analysis")


if submitted:
    if uploaded_file is None:
        form.error("Please, upload the historical data")
    elif len(exp_options) == 0:
        form.error("Please, choose some **type of parallel experiments**")
    elif len(city_option) == 0:
        form.error("Please, choose some city")
    elif len(API_key) == 0:
        form.error("Please, enter your Open Weather API key")
    else:
        flag = True

if flag:
    st.markdown("")
    make_experiments(API_key, exp_options, pos_cities_options)
    curr_city_temp = access_one_city_temp(city_name=city_option, api_key=API_key)
    st.markdown("")
    perform_analysis(data, city_option, curr_city_temp)

if __name__ == '__main__':
    pass


