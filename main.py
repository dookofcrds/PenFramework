import subprocess
import os
import logging
import requests
from colorama import Fore, Style, init as colorama_init
from PyInquirer import prompt  # Assuming you've installed PyInquirer
from dradis import aggregate_results  # Assuming dradis.py is in the same directory

class PenetrationTestingFramework:
    def __init__(self, target):
        self.target = target
        self.output_dir = 'results'
        os.makedirs(self.output_dir, exist_ok=True)
        logging.basicConfig(level=logging.INFO)
        colorama_init(autoreset=True)  # Initialize colorama with autoreset to automatically reset color after each print

    def run_command(self, command, display_output=True):
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            while process.poll() is None:
                output = process.stdout.readline().strip()
                if output:
                    if display_output:
                        print(Fore.CYAN + output + Style.RESET_ALL)
                    logging.info(output)

            _, stderr = process.communicate()

            if stderr:
                print(Fore.RED + stderr + Style.RESET_ALL)
                logging.error(stderr)
                return None

            return process.returncode
        except subprocess.CalledProcessError as e:
            logging.error(f"{Fore.RED}Error running {command[0]}: {e}{Style.RESET_ALL}")
            return None

    def run_amass(self, custom_config=''):
        logging.info(f"\nRunning Amass with custom configurations: {custom_config}")
        command = ['amass', 'enum', '-d', self.target, custom_config]
        return self.run_command(command)

    def run_nmap(self, custom_config=''):
        logging.info(f"\nRunning Nmap with custom configurations: {custom_config}")
        command = ['nmap', self.target, custom_config]
        return self.run_command(command)

    def run_nuclei(self):
        logging.info(f"\nRunning Nuclei with default configurations...")
        command = ['nuclei', self.target]
        return self.run_command(command)

    def generate_report(self, tool_name, tool_output):
        print(Fore.MAGENTA)  # Set text color to magenta
        logging.info(f"\nGenerating report for {tool_name}...")

        if tool_output is not None:
            report_path = os.path.join(self.output_dir, f'{tool_name.lower()}_report.txt')
            with open(report_path, 'w') as report_file:
                report_file.write(tool_output)
            logging.info(f"{tool_name} Report generated successfully.")
        else:
            logging.warning(f"{Fore.YELLOW}No output to generate a report for {tool_name}.{Style.RESET_ALL}")

        print(Style.RESET_ALL)  # Reset text color

    def upload_to_dradis(self, findings):
        dradis_url = "https://your.dradis.instance/api"
        project_id = "your_project_id"
        api_key = "your_api_key"

        headers = {
            "Content-Type": "application/json",
            "api_key": api_key,
        }

        data = {
            "finding": findings,
            # Include any other necessary data for the Dradis API
        }

        try:
            response = requests.post(f"{dradis_url}/projects/{project_id}/findings", json=data, headers=headers, timeout=10)

            if response.status_code == 201:
                logging.info(f"{Fore.GREEN}Findings uploaded to Dradis successfully.{Style.RESET_ALL}")
            else:
                logging.error(f"{Fore.RED}Error uploading findings to Dradis. Status code: {response.status_code}{Style.RESET_ALL}")
        except requests.Timeout:
            logging.error(f"{Fore.RED}Timeout: Unable to connect to the Dradis API. Check your connection and try again.{Style.RESET_ALL}")

    def run_tools(self, selected_tools):
        for tool in selected_tools:
            if tool == 'Amass':
                output = self.run_amass()
                self.generate_report('Amass', output)
            elif tool == 'Nmap':
                output = self.run_nmap()
                self.generate_report('Nmap', output)
            elif tool == 'Nuclei':
                output = self.run_nuclei()
                self.generate_report('Nuclei', output)

        # Aggregate results before uploading to Dradis
        aggregated_results = aggregate_results(self.output_dir)

        # Upload findings to Dradis
        self.upload_to_dradis(aggregated_results)

    def interactive_user_interface(self):
        questions = [
            {
                'type': 'checkbox',
                'name': 'tools',
                'message': f'Select tools to run:',
                'choices': [
                    {'name': 'Amass'},
                    {'name': 'Nmap'},
                    {'name': 'Nuclei'}
                ],
            }
        ]

        answers = prompt(questions)
        selected_tools = answers['tools']
        self.run_tools(selected_tools)

if __name__ == "__main__":
    try:
        target = input(f"{Fore.YELLOW}Enter the target domain or IP:{Style.RESET_ALL} ")

        pt_framework = PenetrationTestingFramework(target)
        pt_framework.interactive_user_interface()
    except Exception as e:
        logging.exception(f"{Fore.RED}An unexpected error occurred: {e}{Style.RESET_ALL}")
