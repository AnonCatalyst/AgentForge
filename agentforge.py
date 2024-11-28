import os
import random
import asyncio
import aiohttp
from fake_useragent import UserAgent
from aiohttp import ClientSession, ClientTimeout
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Asynchronous function to validate a user agent
async def validate_user_agent(agent, session: ClientSession):
    headers = {'User-Agent': agent}
    try:
        async with session.get('https://httpbin.org/user-agent', headers=headers, timeout=5) as response:
            return response.status == 200
    except Exception:
        return False


# Asynchronous function to process user agents in batches
async def process_user_agents(user_agents, batch_size=100):
    valid_agents = []
    total_agents = len(user_agents)
    timeout = ClientTimeout(total=10, connect=5, sock_connect=5, sock_read=5)

    # Create an aiohttp ClientSession for HTTP requests
    async with aiohttp.ClientSession(timeout=timeout) as session:
        for i in range(0, total_agents, batch_size):
            batch = user_agents[i:i + batch_size]
            tasks = [validate_user_agent(agent, session) for agent in batch]
            results = await asyncio.gather(*tasks)

            # Update valid agents list based on results
            valid_agents.extend([agent for agent, valid in zip(batch, results) if valid])

            # Display live status (will only show valid agents)
            display_live_status(total_agents, len(valid_agents), valid_agents)

    return valid_agents


# Function to generate user agents
def generate_user_agents(count=1000):
    ua = UserAgent()
    return [ua.random for _ in range(count)]


# Function to save validated user agents to a file
def save_user_agents(user_agents):
    folder = 'useragents'
    os.makedirs(folder, exist_ok=True)

    file_path = os.path.join(folder, 'useragents.txt')
    with open(file_path, 'w') as file:
        for agent in user_agents:
            file.write(agent + '\n')

    return file_path


# Function to display the live status in a table format
def display_live_status(total_count, valid_count, valid_agents):
    os.system('cls' if os.name == 'nt' else 'clear')  # Clears the console screen for updated live view
    valid_percentage = (valid_count / total_count) * 100

    # Directory and file size information
    file_path = os.path.join('useragents', 'useragents.txt')
    file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
    file_size_readable = f"{file_size / 1024:.2f} KB"  # Convert to KB

    # Live status table - Only show the first 5 valid agents
    print(f"\n{Fore.GREEN + '-'*50}")
    print(f"{Fore.YELLOW + 'Index':<10} {Fore.YELLOW + 'User-Agent'}")
    print(f"{'-'*50}")

    # Display only the first 5 valid agents in the table
    for idx, agent in enumerate(valid_agents[:5], start=1):
        print(f"{Fore.CYAN + str(idx):<10} {Fore.WHITE + agent}")

    print(f"{'-'*50}")
    print(f"{Fore.MAGENTA + 'Processed:':<15} {total_count} | {Fore.MAGENTA + 'Valid:':<10} {valid_count} ({valid_percentage:.2f}%)")  # Status at the bottom
    print(f"{Fore.CYAN + 'Output Directory:':<15} {Fore.GREEN + os.path.abspath('useragents')}")
    print(f"{Fore.CYAN + 'File Size:':<15} {Fore.GREEN + file_size_readable}")
    print(f"{'-'*50}")


# Main function to run the whole process
async def main():
    # User input for how many user agents to generate
    count = int(input(Fore.CYAN + "Enter the number of user agents to generate: "))
    user_agents = generate_user_agents(count)  # Generate user agents
    valid_agents = await process_user_agents(user_agents)  # Validate user agents
    file_path = save_user_agents(valid_agents)  # Save validated user agents

    print(f"{Fore.GREEN + 'Process Complete!'} Valid user agents saved to: {file_path}")


# Run the script
if __name__ == "__main__":
    asyncio.run(main())
