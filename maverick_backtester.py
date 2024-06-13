import streamlit as st

def calculate_profits(grid_profit, initial_investment, num_positions):
    # Convert grid profit percentage to a decimal
    grid_profit_decimal = grid_profit / 100
    # Initialize variables to track realized and unrealized profits
    total_investment = initial_investment
    realized_profit = 0
    unrealized_profit = 0
    
    # List to store profit per position
    unrealized_profits_per_position = [0] * num_positions

    for i in range(num_positions):
        if i == 0:
            profit = total_investment * grid_profit_decimal
        else:
            profit = (total_investment + sum(unrealized_profits_per_position[:i])) * grid_profit_decimal
        unrealized_profits_per_position[i] = profit
        total_investment += profit

    unrealized_profit = sum(unrealized_profits_per_position[:-1])
    realized_profit = unrealized_profits_per_position[-1]

    return realized_profit, unrealized_profit, unrealized_profits_per_position

# Streamlit interface
st.title('Grid Bot Strategy Profit Calculator')

# User inputs
grid_profit = st.number_input('Grid Profit Percentage', min_value=0.01, value=0.21, step=0.01)
initial_investment = st.number_input('Initial Investment ($)', min_value=1.0, value=350.0, step=1.0)
num_positions = st.number_input('Number of Positions', min_value=1, value=14, step=1)

# Calculate profits
realized_profit, unrealized_profit, unrealized_profits_per_position = calculate_profits(grid_profit, initial_investment, num_positions)

# Display results
st.subheader('Results')
st.write(f"Total Realized Profit: ${realized_profit:.2f}")
st.write(f"Total Unrealized Profit: ${unrealized_profit:.2f}")
st.write(f"Total Profit: ${realized_profit + unrealized_profit:.2f}")

st.subheader('Unrealized Profit per Position')
for i, profit in enumerate(unrealized_profits_per_position, start=1):
    st.write(f"Position {i}: ${profit:.2f}")

# Run the Streamlit app
if __name__ == '__main__':
    st.write("Welcome to the Grid Bot Strategy Profit Calculator!")
