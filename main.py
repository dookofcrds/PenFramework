import subprocess
import os
from PyInquirer import prompt  # Assuming you've installed PyInquirer

class PenetrationTestingFramework:
    def __init__(self, target):
        self.target = target
        self.output_dir = 'results'
        os.makedirs(self.output_dir, exist_ok=True)

    def run_command(self, command):
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error running {command[0]}: {e}")
            return None

    def run_amass(self, custom_config=''):
        print("\nRunning Amass with custom configurations:", custom_config)
        command = ['amass', 'enum', '-d', self.target, custom_config]
        result = self.run_command(command)
        if result:
            print("Amass Output:", result)
        return result

    def run_nmap(self, custom_config=''):
        print("\nRunning Nmap with custom configurations:", custom_config)
        command = ['nmap', self.target, custom_config]
        result = self.run_command(command)
        if result:
            print("Nmap Output:", result)
        return result

    def run_nuclei(self):
        print("\nRunning Nuclei with default configurations...")
        command = ['nuclei', self.target]
        result = self.run_command(command)
        if result:
            print("Nuclei Output:", result)
        return result

    def generate_report(self, tool_name, tool_output):
        print(f"\nGenerating report for {tool_name}...")
        report_path = os.path.join(self.output_dir, f'{tool_name.lower()}_report.txt')
        with open(report_path, 'w') as report_file:
            report_file.write(tool_output)
        print(f"{tool_name} Report generated successfully.")

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

    def interactive_user_interface(self):
        questions = [
            {
                'type': 'checkbox',
                'name': 'tools',
                'message': 'Select tools to run:',
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
    target = input("Enter the target domain or IP: ")

    pt_framework = PenetrationTestingFramework(target)
    pt_framework.interactive_user_interface()
