import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import plotly.graph_objects as go
import plotly.express as px

# ✅ MUST be the first Streamlit call
st.set_page_config(layout="wide", page_title="Transaction Dashboard", page_icon="📊")

# --- Appearance Customization ---
st.markdown("""
    <style>
        body {
            background-color: #f9f9f9;
            color: #333;
            font-family: 'Segoe UI', sans-serif;
        }
        h1, h2, h3, h4 {
            color: #003366;
        }
        .block-container {
            padding: 2rem 2rem;
        }
        .css-1d391kg {
            text-align: center;
            color: #2c3e50;
        }
        .dataframe {
            background-color: #ffffff;
            border-radius: 10px;
            border: 1px solid #ddd;
        }
        .stTabs [role="tab"] {
            background-color: #e0e0e0;
            padding: 8px;
            border-radius: 6px;
            margin-right: 8px;
        }
        .stTabs [role="tab"][aria-selected="true"] {
            background-color: #003366;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# --- Dashboard Title ---
st.title("📊 Transaction Analysis Dashboard")

# File Paths
folder_path = r"C:\Users\CGSPL\Desktop\teja\Teja\Teja\IB Reports\IB Reports\IBbank"
file_name = "MERCHANT_TRANSACTION_REPORT_UPDATED.xlsx"
file_path = os.path.join(folder_path, file_name)

folder_path1 = r"C:\Users\CGSPL\Desktop\teja\Teja\Teja\IB Reports\IB Reports\IBbank"
file_name1 = "Combined_QR_Transfer_Reportupdate.csv"
file_path1 = os.path.join(folder_path1, file_name1)


df1 = pd.read_csv(file_path1, skiprows=1, low_memory=False)

# Remove 'Unnamed' columns that come from blank columns or extra separators
df1 = df1.loc[:, ~df1.columns.str.contains('^Unnamed')]

# Clean column names to avoid issues with whitespace or hidden characters
df1.columns = df1.columns.map(str).str.strip().str.replace('\ufeff', '', regex=False).str.upper()


columns_to_drop = [
    'CUST_REF_ID', 'BILL_NO', 'CBS_REF', 'CBS_RRNO', 'QR_ID', 'QR_NAME',
    'WALLET_RRNO', 'CUSTOMER_DISCOUNT', 'BANK_COMMISSION',
    'CUSTOMER_DISCOUNT_AMOUNT', 'BANK_COMMISSION_AMOUNT',
    'SETTLEMENT_ACCOUNT'
]

# Load Data
if os.path.exists(file_path):
    xls = pd.ExcelFile(file_path)
    df = pd.read_excel(xls, sheet_name=xls.sheet_names[0])
    df.columns = df.columns.map(str).str.strip()
    drop_cols = [col for col in columns_to_drop if col in df.columns]
    df.drop(columns=drop_cols, inplace=True)

    df['TXN_CCY'] = df['TXN_CCY'].astype(str).str.strip()
    df['TXN_ID'] = df['TXN_ID'].fillna('FAILED_TXN')
    df['PAY_AMOUNT'] = df['PAY_AMOUNT'].replace({',': ''}, regex=True).astype(float)
    df['PAY_AMOUNT'] = df['PAY_AMOUNT'].fillna(0)
    df.loc[(df['STATUS'] == 'FAILED') & (df['PAY_AMOUNT'].isna()), 'PAY_AMOUNT'] = 0
    df['REASON'] = df['REASON'].replace(["NA", "na", "NaN", "NAN"], np.nan)
    df['TXN_DATE'] = pd.to_datetime(df['TXN_DATE'], errors='coerce')

    failed_df = df[df['STATUS'].str.upper() != 'SUCCESS'].copy()
    failed_df = failed_df[failed_df['REASON'].notna()]
    failed_df['DATE'] = failed_df['TXN_DATE'].dt.date
    failed_df['MONTH'] = failed_df['TXN_DATE'].dt.to_period("M").astype(str)
    failed_df['HOUR'] = failed_df['TXN_DATE'].dt.hour


    daily_group = failed_df.groupby("DATE")
    monthly_group = failed_df.groupby("MONTH")
    hourly_group = failed_df.groupby("HOUR")
    


    # Cleaning the 'AMOUNT' column (removing commas and converting to float)
    df['AMOUNT'] = df['AMOUNT'].replace({',': ''}, regex=True).astype(float)

    # Similarly, clean the 'PAY_AMOUNT' column if needed
    df['PAY_AMOUNT'] = df['PAY_AMOUNT'].replace({',': ''}, regex=True).astype(float)

    # Currency to rate dictionary
    currency_to_rate = {
        'LAK': 1,      # 1 LAK = 1 LAK
        'USD': 21535,  # Example: 1 USD = 21535.65 LAK
        'THB': 645,    # Example: 1 THB = 645 LAK
    }

    # Function to convert the amount to LAK based on the currency
    def convert_to_lak(row):
        currency = row['TXN_CCY']
        exchange_rate = currency_to_rate.get(currency, 1)  # Default to 1 if currency not in the dict
        return row['AMOUNT'] * exchange_rate, row['PAY_AMOUNT'] * exchange_rate
    
    df[['AMOUNT_LAK', 'PAY_AMOUNT_LAK']] = df.apply(convert_to_lak, axis=1, result_type='expand')

    tab1, tab2, tab3, tab4, tab5, tab6= st.tabs([
            "📈 Overview",
            "🏪 Merchant Analytics",
            "👤 Customer Analytics",
            "❌ Failed Transaction Analysis",
            "📊 Detailed Failure Analytics",
            "📥 LMPS-IN Transactions"
        ])
    with tab1:
        st.subheader("✅ Transaction Status Overview")
        failed_count = (df['STATUS'] == 'FAILED').sum()
        success_count = (df['STATUS'] == 'SUCCESS').sum()
        fig1, ax1 = plt.subplots()
        ax1.bar(['Failed', 'Success'], [failed_count, success_count], color=['red', 'green'])
        ax1.set_ylabel("Transaction Count")
        ax1.set_title("Failed vs Successful Transactions")
        for i, val in enumerate([failed_count, success_count]):
            ax1.text(i, val + 5, str(val), ha='center', fontweight='bold')
        st.pyplot(fig1)

       

        st.subheader("💱 Currency-wise Transaction Volume")
        currency_counts = df['TXN_CCY'].value_counts()
        fig5, ax5 = plt.subplots(figsize=(10, 6))
        currency_counts.plot(kind='bar', color=['blue', 'green', 'orange'], ax=ax5)
        ax5.set_title('Total Transactions per Currency', fontsize=16)
        ax5.set_xlabel('Currency', fontsize=12)
        ax5.set_ylabel('Number of Transactions', fontsize=12)
        for i, v in enumerate(currency_counts):
            ax5.text(i, v + 1000, str(v), ha='center', va='bottom', fontsize=12)
        plt.tight_layout()
        st.pyplot(fig5)

        
        

        # Assuming 'df' is already loaded and processed

        # Extract year and month
        df['Month'] = df['TXN_DATE'].dt.to_period('M').astype(str)

        # Total transactions per month
        total_txns = df.groupby('Month').size()

        # Failed transactions per month
        failed_txns = df[df['STATUS'].str.lower() == 'failed'].groupby('Month').size()

        # Combine into one DataFrame
        txn_summary = pd.DataFrame({
            'Total Transactions': total_txns,
            'Failed Transactions': failed_txns
        }).fillna(0).reset_index().rename(columns={'index': 'Month'})

        # Streamlit layout
        # st.title('Transaction Dashboard')

        # 💱 Monthly Total vs Failed Transactions Bar Chart
        st.subheader('📊 Monthly Total vs Failed Transactions')

        # Plot using Plotly
        fig = go.Figure(data=[
            go.Bar(name='Total Transactions', x=txn_summary['Month'], y=txn_summary['Total Transactions'],
                text=txn_summary['Total Transactions'], hoverinfo='text'),
            go.Bar(name='Failed Transactions', x=txn_summary['Month'], y=txn_summary['Failed Transactions'],
                text=txn_summary['Failed Transactions'], hoverinfo='text')
        ])

        fig.update_layout(
            title='Monthly Total vs Failed Transactions',
            xaxis_title='Month',
            yaxis_title='Number of Transactions',
            barmode='group',
            hovermode='x unified',
            template='plotly_white'
        )

        st.plotly_chart(fig)

        # Optionally, show the DataFrame with summary data
        st.subheader('🔍 Monthly Transaction Summary')
        st.dataframe(txn_summary)



    with tab2:
            import plotly.express as px

            st.subheader("🏷️ Number of Transactions by Business Type")

            # Count business types
            business_type_counts = df['BUSINESS_TYPE'].value_counts().reset_index()
            business_type_counts.columns = ['BUSINESS_TYPE', 'TRANSACTION_COUNT']

            # Interactive bar chart
            fig = px.bar(
                business_type_counts,
                x='BUSINESS_TYPE',
                y='TRANSACTION_COUNT',
                color='BUSINESS_TYPE',
                title='Number of Transactions by Business Type',
                labels={'TRANSACTION_COUNT': 'Number of Transactions'},
                color_discrete_sequence=px.colors.qualitative.Set2
            )

            fig.update_layout(
                xaxis_title='Business Type',
                yaxis_title='Number of Transactions',
                xaxis_tickangle=-45,
                showlegend=False,
                height=500
            )

            st.plotly_chart(fig, use_container_width=True)


            df_filtered = df[df['TXN_ID'] != 'FAILED_TXN']

            # Ensure that AMOUNT_LAK is numeric
            df_filtered['AMOUNT_LAK'] = pd.to_numeric(df_filtered['AMOUNT_LAK'], errors='coerce')
            st.subheader("Top Performing Merchants Based on Total Transaction Amount")
            # Group by merchant and sum the transaction amounts
            merchant_total_amount = df_filtered.groupby('MERCHANT_NAME')['AMOUNT_LAK'].sum()

            # Sort the merchants by total transaction amount in descending order and select the top 10
            top_merchants = merchant_total_amount.sort_values(ascending=False).head(10)

            # Plot the pie chart for the top-performing merchants
            plt.figure(figsize=(8, 8))
            top_merchants.plot(kind='pie', autopct='%1.1f%%', colors=plt.cm.Paired.colors, legend=False, labels=top_merchants.index)
            
            plt.ylabel('')  # Hide the y-label
            plt.show()
            st.pyplot(plt)

                # ---- Unique Merchants Count per MEMBER_ID ----
            import plotly.express as px

            st.subheader("🛒 Unique Merchants Count per MEMBER_ID")

            # Group by MEMBER_ID and count unique merchants
            merchant_grouping = df.groupby('MEMBER_ID')['MERCHANT_NAME'].nunique().reset_index()
            merchant_grouping = merchant_grouping.rename(columns={'MERCHANT_NAME': 'Unique_Merchants_Count'})

            # Sort in descending order
            merchant_grouping = merchant_grouping.sort_values(by='Unique_Merchants_Count', ascending=False)

            # Interactive Plot
            fig = px.bar(
                merchant_grouping,
                x='MEMBER_ID',
                y='Unique_Merchants_Count',
                title='Unique Merchants Count per MEMBER_ID',
                labels={'MEMBER_ID': 'Member ID', 'Unique_Merchants_Count': 'Unique Merchants'},
                color='Unique_Merchants_Count',
                color_continuous_scale='Viridis'
            )

            fig.update_layout(
                xaxis_tickangle=-45,
                height=500
            )

            st.plotly_chart(fig, use_container_width=True)


                # ---- Top 10 Merchants by Transaction Count ----
            import plotly.express as px

            st.subheader("🏪 Top 10 Merchants by Transaction Count")

            # Count transaction occurrences for each merchant
            merchant_txn_counts = df['MERCHANT_NAME'].value_counts().reset_index()
            merchant_txn_counts.columns = ['MERCHANT_NAME', 'Transaction_Count']

            # Get Top 10 Merchants by transaction count
            top_merchants = merchant_txn_counts.head(10)

            # Interactive bar chart using Plotly
            fig = px.bar(
                top_merchants,
                x='Transaction_Count',
                y='MERCHANT_NAME',
                orientation='h',
                title='Top 10 Merchants by Number of Transactions',
                color='Transaction_Count',
                color_continuous_scale='RdBu'
            )

            fig.update_layout(
                yaxis=dict(autorange="reversed"),  # To show highest at the top
                xaxis_title="Number of Transactions",
                yaxis_title="Merchant Name",
                height=500
            )

            st.plotly_chart(fig, use_container_width=True)

            # Compute transaction counts per merchant
            merchant_counts = df['MERCHANT_NAME'].value_counts()

            # Get bottom 10 merchants
            least_merchants = merchant_counts.tail(10)

            # Streamlit header
            st.subheader("10 Least Performing Merchants")

            # Show data in a table
            st.dataframe(
                least_merchants.reset_index().rename(
                    columns={'index': 'Merchant Name', 'MERCHANT_NAME': 'Transaction Count'}
                )
            )

            # Plot bar chart with color
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(x=least_merchants.values, y=least_merchants.index, palette="Set2", ax=ax)
            ax.set_xlabel("Number of Transactions")
            ax.set_ylabel("Merchant Name")
            ax.set_title("10 Least Performing Merchants")
            st.pyplot(fig)


            df['TXN_DATE'] = pd.to_datetime(df['TXN_DATE'], errors='coerce')
            df = df.dropna(subset=['TXN_DATE'])
            df['TXN_MONTH'] = df['TXN_DATE'].dt.to_period('M').astype(str)

            # Count transactions per merchant per month
            monthly_merchant_counts = (
                df.groupby(['TXN_MONTH', 'MERCHANT_NAME'])
                .size()
                .reset_index(name='TXN_COUNT')
            )

            # Get top 5 merchants per month
            top_5_per_month = (
                monthly_merchant_counts
                .sort_values(['TXN_MONTH', 'TXN_COUNT'], ascending=[True, False])
                .groupby('TXN_MONTH')
                .head(5)
                .reset_index(drop=True)
            )

            # Add merchant mobile numbers
            merchant_mobiles = df[['MERCHANT_NAME', 'MERCHANT_MOBILE']].dropna().drop_duplicates()
            top_5_per_month = pd.merge(top_5_per_month, merchant_mobiles, on='MERCHANT_NAME', how='left')

            # Label with name + mobile
            top_5_per_month['MERCHANT_LABEL'] = (
                top_5_per_month['MERCHANT_NAME'] + '\n📞' + top_5_per_month['MERCHANT_MOBILE'].astype(str)
            )

            # Plotly bar chart
            fig = px.bar(
                top_5_per_month,
                x="TXN_MONTH",
                y="TXN_COUNT",
                color="MERCHANT_LABEL",
                title="Top 5 Merchants by Transaction Count for Each Month",
                labels={"TXN_COUNT": "Transaction Count", "TXN_MONTH": "Month"},
                barmode="group",
                height=600,
                color_discrete_sequence=px.colors.qualitative.Set2
            )

            fig.update_layout(
                xaxis_tickangle=-45,
                legend_title_text="Merchant (Name & Mobile)",
                margin=dict(l=40, r=20, t=60, b=80)
            )

            # Show in Streamlit
            st.subheader('📊 Top 5 Merchants by Transaction Count for Each Month')
            st.plotly_chart(fig, use_container_width=True)


            # Ensure TXN_DATE is in datetime format
            df['TXN_DATE'] = pd.to_datetime(df['TXN_DATE'], format='%d-%b-%y %H:%M:%S', errors='coerce')
            df = df.dropna(subset=['TXN_DATE'])

            # Extract daily and monthly time features
            df['TXN_DAY'] = df['TXN_DATE'].dt.date
            df['TXN_MONTH'] = df['TXN_DATE'].dt.to_period('M')

            # Get top 5 merchants by overall transaction volume
            top_merchants = df['MERCHANT_NAME'].value_counts().head(5).index

            # Compute daily transaction trend
            daily_trend = (
                df[df['MERCHANT_NAME'].isin(top_merchants)]
                .groupby(['MERCHANT_NAME', 'TXN_DAY'])
                .size()
                .reset_index(name='Transaction_Count')
            )

            # 📊 Interactive Line Plot - All top merchants in one chart
            st.subheader("📈 Daily Transaction Trend for Top 5 Merchants")

            fig = px.line(
                daily_trend,
                x='TXN_DAY',
                y='Transaction_Count',
                color='MERCHANT_NAME',
                markers=True,
                title='📈 Daily Transactions of Top Merchants',
                labels={'TXN_DAY': 'Transaction Date', 'Transaction_Count': 'Transaction Count'},
                template='plotly_white'
            )

            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

            # 📊 Optional: One chart per merchant (expandable section)
            with st.expander("📊 See Individual Merchant Trends"):
                for merchant in top_merchants:
                    merchant_data = daily_trend[daily_trend['MERCHANT_NAME'] == merchant]

                    fig_ind = px.line(
                        merchant_data,
                        x='TXN_DAY',
                        y='Transaction_Count',
                        title=f'Daily Transactions for {merchant}',
                        markers=True,
                        labels={'TXN_DAY': 'Transaction Date', 'Transaction_Count': 'Transactions'},
                        template='plotly_white'
                    )
                    fig_ind.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig_ind, use_container_width=True)

           
            # ---- Inactive Merchants in the Last 3 Months ----
            st.subheader('📴 Inactive Merchants in the Last 3 Months')

            # Ensure TXN_DATE is parsed properly
            df['TXN_DATE'] = pd.to_datetime(df['TXN_DATE'], errors='coerce')

            # Drop rows with invalid TXN_DATE
            df = df.dropna(subset=['TXN_DATE'])

            # Set cutoff date to 3 months ago
            cutoff_date = pd.Timestamp.today() - pd.DateOffset(months=3)

            # Filter transactions in the last 3 months
            recent_txns = df[df['TXN_DATE'] >= cutoff_date]

            # Get active merchants
            active_merchants = recent_txns['MERCHANT_NAME'].dropna().unique()

            # Get all merchants
            all_merchants = df['MERCHANT_NAME'].dropna().unique()

            # Identify inactive merchants
            inactive_merchants = list(set(all_merchants) - set(active_merchants))

            # Get unique merchant-mobile pairs from original data
            merchant_mobile_map = df[['MERCHANT_NAME', 'MERCHANT_MOBILE']].dropna().drop_duplicates()

            # Filter for inactive merchants
            inactive_df = merchant_mobile_map[merchant_mobile_map['MERCHANT_NAME'].isin(inactive_merchants)]

            # Rename columns for clarity
            inactive_df = inactive_df.rename(columns={'MERCHANT_NAME': 'INACTIVE_MERCHANT_NAME', 'MERCHANT_MOBILE': 'MOBILE_NUMBER'})

            # Display inactive merchants with mobile numbers in the Streamlit app
            st.write("Inactive merchants in the last 3 months with mobile numbers:")

            # Display top few inactive merchants
            st.dataframe(inactive_df.head(10))

    with tab3:
            top_10_merchants = (
            df['MERCHANT_NAME'].value_counts().head(10).index.tolist()
    ) 
            # ---- Top Customers Per Merchant (Top 3) ----
            st.subheader("👥 Top 3 Customers for Each Merchant")

            # Compute transaction count per customer per merchant
            top_customers_per_merchant = (
                df[df['MERCHANT_NAME'].isin(top_10_merchants)]
                .groupby(['MERCHANT_NAME', 'USER_MOBILE'])
                .size()
                .reset_index(name='txn_count')
            )

            # For each merchant, get top 3 customers
            top_customers = (
                top_customers_per_merchant
                .sort_values(['MERCHANT_NAME', 'txn_count'], ascending=[True, False])
                .groupby('MERCHANT_NAME')
                .head(3)  # Top 3 customers per merchant
            )

            # Display the list of top customers for each merchant
            st.dataframe(top_customers)

            # ---- Transaction Trend for Top Customers Over Time ----
            st.subheader("📈 Transaction Trends Over Time - Top Customers")

            # Sort user mobiles by total transactions for consistent hue order

            merged_top_customers = pd.merge(
                df,
                top_customers[['MERCHANT_NAME', 'USER_MOBILE']],
                on=['MERCHANT_NAME', 'USER_MOBILE'],
                how='inner'
            )
            top_users_ordered = (
                merged_top_customers.groupby('USER_MOBILE')
                .size()
                .sort_values(ascending=False)
                .index
            )

            # Plot: Sorted by mobile number performance (txn count)
            for merchant in merged_top_customers['MERCHANT_NAME'].unique():
                plt.figure(figsize=(12, 6))
                temp = merged_top_customers[merged_top_customers['MERCHANT_NAME'] == merchant]

                # Order the hue based on overall frequency
                sns.lineplot(
                    data=temp,
                    x='TXN_DATE',
                    y='PAY_AMOUNT',
                    hue='USER_MOBILE',
                    hue_order=[u for u in top_users_ordered if u in temp['USER_MOBILE'].unique()],
                    marker='o'
                )

                plt.title(f"Transaction Trend Over Time - Top Customers of {merchant}")
                plt.xlabel("Date")
                plt.ylabel("Pay Amount")
                plt.xticks(rotation=45)
                plt.legend(title='User Mobile', bbox_to_anchor=(1.05, 1), loc='upper left')
                plt.tight_layout()
                st.pyplot(plt)
    
    with tab4:
        
        
            st.subheader("❌ Failed Transactions Overview")

            # --- Clean & Preprocess ---
            df["REASON"] = df["REASON"].astype(str).str.strip().str.upper()
            df["TXN_DATE"] = pd.to_datetime(df["TXN_DATE"], errors='coerce')

            # Replace known bad REASONs
            reasons_to_replace = [
                "CONNECTION_ERROR",
                "NO,HOLD - OVERRIDE SAME DEBIT AND CREDIT ACCOUNT",
                "NO,DEBIT.ACCT.NO:1:1=JOINT_ACCT_NOT_ALLOW,DEBIT.ACCT.NO:1:1=JOINT_ACCT_NOT_ALLOW",
                "INVALID_SIGN_ON_NAME_OR PASSWORD",
                "NO,HOLD - OVERRIDE EXCEEDED MORE THAN 2 WITHDRAWALS IN ONE MONTH",
                "NO,CREDIT.AMOUNT:1:1=FT-VAL.AMOUNT.SHOULD.NOT.BE.ZERO"
                "NO,HOLD - OVERRIDE Account 0100001651657 - Post no Debit"
            ]
            df.loc[
                (df['REASON'].isin(reasons_to_replace)) & (df['PAYMENT_MODE'].str.upper() == 'ACCOUNT'),
                'REASON'
            ] = "BAD RESPONSE FROM CBS"

            # Define failed_df correctly
            failed_df = df[df["STATUS"].str.upper() == "FAILED"].copy()

            # Time-based columns
            failed_df["DATE"] = failed_df["TXN_DATE"].dt.date
            failed_df["MONTH"] = failed_df["TXN_DATE"].dt.to_period("M").astype(str)
            failed_df["HOUR"] = failed_df["TXN_DATE"].dt.hour

            # --- Daily Failed Transactions ---
            st.subheader('📉 Daily Failed Transactions')
            daily_counts = failed_df.groupby("DATE").size().reset_index(name="Failed_Count")
            fig_daily = px.line(daily_counts, x="DATE", y="Failed_Count", markers=True,
                                title="Daily Failed Transactions",
                                labels={"DATE": "Date", "Failed_Count": "Number of Failed Transactions"},
                                color_discrete_sequence=["#EF553B"])
            st.plotly_chart(fig_daily)

            # --- Monthly Failed Transactions ---
            st.subheader('📊 Monthly Failed Transactions')
            monthly_counts = failed_df.groupby("MONTH").size().reset_index(name="Failed_Count")
            fig_month = px.bar(monthly_counts, x="MONTH", y="Failed_Count",
                            title="Monthly Failed Transactions",
                            labels={"MONTH": "Month", "Failed_Count": "Count"},
                            color_discrete_sequence=["#636EFA"])
            st.plotly_chart(fig_month)

            # --- Hourly Failed Transactions ---
            st.subheader('⏰ Hourly Failed Transactions')
            hourly_counts = failed_df.groupby("HOUR").size().reset_index(name="Failed_Count")
            fig_hour = px.bar(hourly_counts, x="HOUR", y="Failed_Count",
                            title="Hourly Failed Transactions",
                            labels={"HOUR": "Hour of Day", "Failed_Count": "Count"},
                            color_discrete_sequence=["#00CC96"])
            st.plotly_chart(fig_hour)

            # --- Failure Reasons Count ---
            st.subheader("📉 Failure Reasons Count")

            # Normalize and clean REASON column
            reason_df = failed_df.copy()
            reason_df["REASON"] = reason_df["REASON"].astype(str).str.strip().str.upper()

            # Replace common bad strings with actual NaN
            reason_df["REASON"] = reason_df["REASON"].replace(
                ["NA", "NAN", "NONE", "SUCESS", ""], pd.NA
            )

            # Filter non-null reasons
            reason_df = reason_df[reason_df["REASON"].notna()]

            # Count reasons
            reason_counts = reason_df['REASON'].value_counts()
            top_reasons = reason_counts[reason_counts > 10].head(6)

            # Plot
            fig2, ax2 = plt.subplots(figsize=(12, 6))
            sns.barplot(x=top_reasons.values, y=top_reasons.index, ax=ax2, palette="Oranges_r")
            ax2.set_xlabel("Count")
            ax2.set_title("Top Failure Reasons")
            st.pyplot(fig2)


            st.subheader("📉 Top Failure Reasons by Payment Mode")

            # Normalize and clean
            reason_df = failed_df.copy()
            reason_df["REASON"] = reason_df["REASON"].astype(str).str.strip().str.upper()
            reason_df["PAYMENT_MODE"] = reason_df["PAYMENT_MODE"].astype(str).str.strip().str.upper()

            # Replace bad strings
            reason_df["REASON"] = reason_df["REASON"].replace(["NA", "NAN", "NONE", "SUCESS", ""], pd.NA)
            reason_df = reason_df[reason_df["REASON"].notna()]

            # Find top 6 overall reasons with more than 10 occurrences
            top6_reasons = (
                reason_df["REASON"].value_counts().loc[lambda x: x > 10].head(6).index.tolist()
            )

            # Filter only top 6 reasons
            filtered_df = reason_df[reason_df["REASON"].isin(top6_reasons)]

            # Separate plots for each payment mode
            for mode in ['ACCOUNT', 'WALLET']:
                mode_df = filtered_df[filtered_df["PAYMENT_MODE"] == mode]
                
                if not mode_df.empty:
                    reason_counts = mode_df["REASON"].value_counts()

                    fig, ax = plt.subplots(figsize=(10, 5))
                    sns.barplot(x=reason_counts.values, y=reason_counts.index, ax=ax, palette="Oranges_r")
                    ax.set_xlabel("Count")
                    ax.set_ylabel("Failure Reason")
                    ax.set_title(f"Top Failure Reasons - {mode}")
                    st.pyplot(fig)
                else:
                    st.info(f"No failure reasons found for payment mode: {mode}")


            # --- Failed Transactions per Currency ---
            st.subheader("💸 Failed Transactions per Currency")
            failed_currency_counts = failed_df['TXN_CCY'].value_counts()
            fig6, ax6 = plt.subplots(figsize=(8, 6))
            failed_currency_counts.plot(kind='bar', color='red', ax=ax6)
            ax6.set_title('Failed Transactions per Currency')
            ax6.set_xlabel('Currency')
            ax6.set_ylabel('Count')
            for i, v in enumerate(failed_currency_counts):
                ax6.text(i, v + 5, str(v), ha='center', fontweight='bold')
            st.pyplot(fig6)

            # --- Failed % by Payment Mode ---
            st.subheader("📉 Failed Transactions % by Payment Mode")
            df_filtered = df[df['PAYMENT_MODE'].fillna('').str.upper() != 'BNPL']
            total_by_mode = df_filtered.groupby('PAYMENT_MODE').size()
            failed_by_mode = df_filtered[df_filtered['STATUS'].str.upper() == 'FAILED'].groupby('PAYMENT_MODE').size()
            failed_percentage = (failed_by_mode / total_by_mode * 100).round(2).sort_values(ascending=False)
            st.dataframe(failed_percentage.reset_index().rename(columns={0: 'Failure %'}))

            fig10, ax10 = plt.subplots(figsize=(6, 8))
            ax10.pie(
                failed_percentage,
                labels=failed_percentage.index,
                autopct='%1.1f%%',
                startangle=140,
                colors=plt.cm.Pastel1.colors
            )
            ax10.set_title("Failed Transactions % by Payment Mode")
            ax10.axis('equal')
            plt.tight_layout()
            st.pyplot(fig10)

            # --- Top 10 Merchants with Most Failed Transactions ---
            st.subheader("🏪 Top 10 Merchants with Most Failed Transactions")
            merchant_failure_counts = failed_df['MERCHANT_NAME'].value_counts().head(5)
            fig3, ax3 = plt.subplots(figsize=(10, 6))
            sns.barplot(x=merchant_failure_counts.values, y=merchant_failure_counts.index, ax=ax3, palette="viridis")
            ax3.set_title("Top 10 Merchants with Most Failed Transactions")
            ax3.set_xlabel("Number of Failed Transactions")
            ax3.set_ylabel("Merchant Name")
            st.pyplot(fig3)

            # --- Top 5 Failure Reasons for Each Top Merchant ---
            st.subheader("🔍 Top 5 Failure Reasons for Each Top Merchant")
            for merchant in merchant_failure_counts.index:
                merchant_reasons = reason_df[reason_df['MERCHANT_NAME'] == merchant]['REASON'].value_counts().head(5)
                st.markdown(f"#### {merchant}")
                fig, ax = plt.subplots(figsize=(10, 4))
                sns.barplot(x=merchant_reasons.values, y=merchant_reasons.index, palette="magma", ax=ax)
                ax.set_title(f"Top 5 Failure Reasons for {merchant}")
                ax.set_xlabel("Count")
                ax.set_ylabel("Reason")
                st.pyplot(fig)

                


    with tab5:
        st.subheader("🔎 Top 3 Failure Reasons by Day")
        for date, group in daily_group:
            top_reasons = group["REASON"].value_counts().head(3)
            st.markdown(f"**{date}**")
            st.write(top_reasons)

        st.subheader("📅 Top 3 Failure Reasons by Month")
        for month, group in monthly_group:
            top_reasons = group["REASON"].value_counts().head(3)
            st.markdown(f"**{month}**")
            st.write(top_reasons)

        st.subheader("🕓 Top 3 Failure Reasons by Hour")
        
        for hour, group in hourly_group:
            top_reasons = group["REASON"].value_counts().head(3)
            st.markdown(f"**Hour {hour}**")
            st.write(top_reasons)

    
    
    with tab6:
        # st.subheader("🏦 Transaction Count Received by each Bank")
        # bank_counts = df1['FROM_MEMBER'].value_counts()

        # fig1, ax1 = plt.subplots(figsize=(10, 5), facecolor='none')
        # ax1.bar(bank_counts.index, bank_counts.values, color='skyblue')
        # ax1.set_title('Transaction Count by Bank (FROM_MEMBER)', fontsize=14)
        # ax1.set_xlabel('Bank')
        # ax1.set_ylabel('Number of Transactions')
        # ax1.tick_params(axis='x', rotation=45)
        # for i, v in enumerate(bank_counts.values):
        #     ax1.text(i, v + 5, str(v), ha='center', va='bottom', fontsize=9)
        # st.pyplot(fig1)

        st.subheader("🏦 Transaction Count Received from each Bank")

        if 'FROM_MEMBER' not in df1.columns:
            # Clean column names: strip, fix BOM, upper-case
            df1.columns = df1.columns.str.strip().str.replace('\ufeff', '', regex=False).str.upper()

        if 'FROM_MEMBER' in df1.columns:
            bank_counts = df1['FROM_MEMBER'].value_counts()

            fig1, ax1 = plt.subplots(figsize=(10, 5), facecolor='none')
            ax1.bar(bank_counts.index, bank_counts.values, color='skyblue')
            ax1.set_title('Transaction Count by Bank (FROM_MEMBER)', fontsize=14)
            ax1.set_xlabel('Bank')
            ax1.set_ylabel('Number of Transactions')
            ax1.tick_params(axis='x', rotation=45)

            for i, v in enumerate(bank_counts.values):
                ax1.text(i, v + 5, str(v), ha='center', va='bottom', fontsize=9)

            st.pyplot(fig1)
        else:
            st.error("❌ 'FROM_MEMBER' column not found. Check uploaded CSV headers.")

        # # SECTION: Payment Mode Distribution (Pie)
        # st.subheader("💰 Payment Mode Type Distribution")
        # settle_pie = df1['SETTLE_TO'].value_counts(dropna=False)
        # fig2, ax2 = plt.subplots(figsize=(6, 6), facecolor='none')
        # ax2.pie(settle_pie.values, labels=settle_pie.index.astype(str), autopct='%1.1f%%', startangle=140, colors=plt.cm.Set3.colors)
        # ax2.axis('equal')
        # st.pyplot(fig2)

        # # SECTION: Payment Mode Count - Plotly
        # st.subheader("💳 Transactions by Payment Mode")
        # settle_types_df = df1['SETTLE_TO'].fillna('NaN').value_counts().reset_index()
        # settle_types_df.columns = ['SETTLE_TO', 'COUNT']
        # fig3 = px.bar(settle_types_df, x='SETTLE_TO', y='COUNT', color='SETTLE_TO', template='plotly_dark',
        #             title='Count of Transactions by Payment Mode (SETTLE_TO)',
        #             labels={'SETTLE_TO': 'Payment Mode', 'COUNT': 'Number of Transactions'})
        # fig3.update_layout(xaxis_tickangle=-45)
        # st.plotly_chart(fig3, use_container_width=True)

        # Clean SETTLE_TO column
        df1['SETTLE_TO'] = df1['SETTLE_TO'].astype(str).str.strip()  # Remove leading/trailing spaces

        # Drop any rows where SETTLE_TO is literally the header string 'SETTLE_TO' (case-insensitive)
        df1 = df1[df1['SETTLE_TO'].str.upper() != 'SETTLE_TO']

        # Replace NaNs with 'Unknown' for cleaner charts
        df1['SETTLE_TO'] = df1['SETTLE_TO'].replace('nan', 'Unknown')



        # # --- PIE CHART ---
        # st.subheader("💰 Payment Mode Type Distribution")
        # settle_pie = df1['SETTLE_TO'].value_counts(dropna=False)
        # fig2, ax2 = plt.subplots(figsize=(6, 6), facecolor='none')
        # ax2.pie(settle_pie.values, labels=settle_pie.index, autopct='%1.1f%%',
        #         startangle=140, colors=plt.cm.Set3.colors)
        # ax2.axis('equal')
        # st.pyplot(fig2)

        # --- BAR CHART (Plotly) ---
        st.subheader("💳 Transactions by Payment Mode")
        settle_types_df = df1['SETTLE_TO'].value_counts().reset_index()
        settle_types_df.columns = ['SETTLE_TO', 'COUNT']

        fig3 = px.bar(
            settle_types_df,
            x='SETTLE_TO',
            y='COUNT',
            color='SETTLE_TO',
            template='plotly_dark',
            title='Count of Transactions by Payment Mode',
            labels={'SETTLE_TO': 'Payment Mode', 'COUNT': 'Number of Transactions'}
        )
        fig3.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig3, use_container_width=True)

        # Clean the fee column
        # df1['TXN_FEE_AMOUNT_CLEAN'] = pd.to_numeric(
        #     df1['TXN_FEE_AMOUNT'].astype(str).str.replace(',', ''), 
        #     errors='coerce'
        # )
        # df1 = df1.dropna(subset=['TXN_FEE_AMOUNT_CLEAN'])

        # # Group by FROM_MEMBER and TO_MEMBER
        # fee_earned = df1.groupby(['FROM_MEMBER', 'TO_MEMBER'])['TXN_FEE_AMOUNT_CLEAN'].sum().reset_index()

        # # Get top 10 fee earning pairs
        # top_fee_pairs = fee_earned.sort_values(by='TXN_FEE_AMOUNT_CLEAN', ascending=False).head(10)
        # top_fee_pairs['PAIR'] = top_fee_pairs['FROM_MEMBER'] + " ➝ " + top_fee_pairs['TO_MEMBER']

        # # Show table
        # st.subheader("Top 10 Fee-Earning Member Pairs")
        # st.dataframe(
        #     top_fee_pairs[['FROM_MEMBER', 'TO_MEMBER', 'TXN_FEE_AMOUNT_CLEAN']]
        #     .rename(columns={'TXN_FEE_AMOUNT_CLEAN': 'Total Fee'})
        # )

        # # Plot
        # fig4, ax4 = plt.subplots(figsize=(12, 6))
        # sns.barplot(
        #     x='TXN_FEE_AMOUNT_CLEAN',
        #     y='PAIR',
        #     data=top_fee_pairs,
        #     palette='Blues_d',
        #     ax=ax
        # )
        # ax4.set_xlabel("Total Transaction Fee")
        # ax4.set_ylabel("From ➝ To")
        # ax4.set_title("Top 10 Fee-Earning Member Pairs")
        # st.pyplot(fig4)

        

        # Clean the fee amount column
        df1['TXN_FEE_AMOUNT_CLEAN'] = pd.to_numeric(
            df1['TXN_FEE_AMOUNT'].astype(str).str.replace(',', ''), 
            errors='coerce'
        )
        df1 = df1.dropna(subset=['TXN_FEE_AMOUNT_CLEAN'])

        # Clean transaction amount column
        df1['TXN_AMOUNT_CLEAN'] = pd.to_numeric(
            df1['TXN_AMOUNT'].astype(str).str.replace(',', ''), 
            errors='coerce'
        )
        df1 = df1.dropna(subset=['TXN_AMOUNT_CLEAN'])

        # Group by FROM_MEMBER (banks that SENT the transactions)
        bank_sent_summary = df1.groupby('FROM_MEMBER').agg(
            Total_Transactions=('TXN_AMOUNT_CLEAN', 'count'),
            Total_Amount=('TXN_AMOUNT_CLEAN', 'sum'),
            Total_Fee=('TXN_FEE_AMOUNT_CLEAN', 'sum')
        ).reset_index()

        # Display in Streamlit
        st.subheader("🏦 Summary of Transactions Sent by Each Bank (FROM_MEMBER)")
        st.dataframe(bank_sent_summary.sort_values(by='Total_Amount', ascending=False))



        # SECTION: Monthly Transaction Count
        st.subheader("📅 Monthly Received Transaction Counts")
        df1['TXN_DATE'] = pd.to_datetime(df1['TXN_DATE'], errors='coerce')
        df1['MONTH'] = df1['TXN_DATE'].dt.to_period('M')  
        

        monthly_counts = df1.groupby('MONTH').size()
        fig5, ax5 = plt.subplots(figsize=(10, 5), facecolor='none')
        sns.barplot(x=monthly_counts.index.astype(str), y=monthly_counts.values, palette='coolwarm', ax=ax5)
        ax5.set_title("Monthly Received Transaction Counts", fontsize=16)
        ax5.set_xlabel("Month")
        ax5.set_ylabel("Number of Transactions")
        for i, val in enumerate(monthly_counts.values):
            ax5.text(i, val + 5, str(val), ha='center', va='bottom', fontweight='bold')
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig5)

        # SECTION: Top 10 Merchants
        st.subheader("🏆 Top 10 Merchants by Number of Transactions Received")
        top_merchants = df1['MERCHANT_NAME'].value_counts().head(10)
        fig6, ax6 = plt.subplots(figsize=(10, 5), facecolor='none')
        sns.barplot(x=top_merchants.values, y=top_merchants.index, palette='viridis', ax=ax6)
        ax6.set_title("Top 10 Merchants by Number of Transactions", fontsize=16)
        ax6.set_xlabel("Number of Transactions")
        ax6.set_ylabel("Merchant")
        for index, value in enumerate(top_merchants.values):
            ax6.text(value + 5, index, str(value), va='center', fontweight='bold')
        st.pyplot(fig6)

        
        st.subheader("📆 Busiest Transaction Day in Each Month")

        # Ensure TXN_DATE is in datetime format
        df["TXN_DATE"] = pd.to_datetime(df["TXN_DATE"], errors='coerce')

        # Drop rows with missing TXN_DATE
        df = df.dropna(subset=["TXN_DATE"])

        # Extract date and month
        df["DATE"] = df["TXN_DATE"].dt.date
        df["MONTH"] = df["TXN_DATE"].dt.to_period("M").astype(str)

        # Count transactions per day
        daily_counts = df.groupby("DATE").size().reset_index(name="Txn_Count")

        # Extract month again from DATE to join later
        daily_counts["MONTH"] = pd.to_datetime(daily_counts["DATE"]).dt.to_period("M").astype(str)

        # For each month, find the date with max transactions
        busiest_days = daily_counts.loc[daily_counts.groupby("MONTH")["Txn_Count"].idxmax()].sort_values("MONTH")

        # Plot
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.barplot(x="MONTH", y="Txn_Count", data=busiest_days, palette="Blues_d")

        # Add date annotations above bars
        for i, row in enumerate(busiest_days.itertuples()):
            ax.text(
                i,
                row.Txn_Count + 2,
                str(row.DATE),
                ha='center',
                va='bottom',
                fontweight='bold'
            )

        ax.set_title("📆 Busiest Transaction Day in Each Month")
        ax.set_xlabel("Month")
        ax.set_ylabel("Number of Transactions")

        st.pyplot(fig)

        

else:
    st.error(f"File not found: {file_path}")

