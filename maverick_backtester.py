import streamlit as st

def calculate_profits(grid_profit, initial_investment, num_positions):
    # Convert grid profit percentage to a decimal
    grid_profit_decimal = grid_profit / 100
    # Initialize variables to track realized and unrealized profits
    realized_profit = 0
    unrealized_profit = 0
    total_investment = initial_investment
    
    # List to store profit per position
    profit_list = []

    for i in range(num_positions):
        # Calculate profit for the current position
        profit = total_investment * grid_profit_decimal
        profit_list.append(profit)
        
        # Update total investment by adding the profit
        total_investment += profit
        
        # Track realized and unrealized profits
        if i < num_positions - 1:
            unrealized_profit += profit
        else:
            realized_profit += profit

    return realized_profit, unrealized_profit, profit_list

# Streamlit interface
st.title('Grid Bot Strategy Profit Calculator')

# User inputs
grid_profit = st.number_input('Grid Profit Percentage', min_value=0.01, value=0.21, step=0.01)
initial_investment = st.number_input('Initial Investment ($)', min_value=1.0, value=350.0, step=1.0)
num_positions = st.number_input('Number of Positions', min_value=1, value=14, step=1)

# Calculate profits
realized_profit, unrealized_profit, profit_list = calculate_profits(grid_profit, initial_investment, num_positions)

# Display results
st.subheader('Results')
st.write(f"Total Realized Profit: ${realized_profit:.2f}")
st.write(f"Total Unrealized Profit: ${unrealized_profit:.2f}")
st.write(f"Total Profit: ${realized_profit + unrealized_profit:.2f}")

st.subheader('Profit per Position')
for i, profit in enumerate(profit_list, start=1):
    st.write(f"Position {i}: ${profit:.2f}")

# Run the Streamlit app
if __name__ == '__main__':
    st.write("Welcome to the Grid Bot Strategy Profit Calculator!")
