import sys

def main():
    print("Welcome to the Interactive CLI for the Agent!")
    while True:
        user_input = input("Please enter a message to check (or type 'exit' to quit): ")
        if user_input.lower() == 'exit':
            print("Exiting the program. Goodbye!")
            break
        # Here you would integrate the interaction with your agent,
        # for demonstration purposes, we're just echoing the input.
        print(f"Checking message: {user_input}")

if __name__ == '__main__':
    main()