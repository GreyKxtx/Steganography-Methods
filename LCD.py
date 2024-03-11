import sys
import os
from PIL import Image, ImageDraw
from cryptography.fernet import Fernet
from colorama import Fore, Style

class LCD:
    def __init__(self):
        self.DATA = dict()
        self.name = sys.argv[0].split('/')[-1]
        self.version = "v0.0.4release"

    def process_action(self, action, image_path, data_path=None, balance=None, key=None):
        try:
            if action == 'encrypt':
                if data_path is None:
                    raise FileNotFoundError("Data file not provided.")

                # Check directory to Data file
                if data_path[0] != '/':
                    data_path = os.getcwd() + '/' + data_path

                if not os.path.exists(data_path):
                    raise FileNotFoundError("Data file not found.")

                # Validate balance
                if balance is not None:
                    value = int(balance)

                    if value < 1 or value > 4:
                        raise ValueError("Balance should be from 1 to 4.")

            elif action == 'decrypt':
                if not os.path.exists(image_path):
                    raise FileNotFoundError("Image file not found.")

                if key is None:
                    raise ValueError("Key not provided.")

        except FileNotFoundError as e:
            self.error(str(e), True)

        except ValueError as e:
            self.error(str(e), True)

        if action == 'encrypt':
            if balance is None:
                try:
                    balance = int(input(Style.BRIGHT + Fore.RED + "     Balance (1 to 4) > "))
                    if balance < 1 or balance > 4:
                        raise ValueError("Invalid balance.")
                except ValueError:
                    self.error("Set to 2.", False)
                    balance = 2

            file = open(data_path, 'r')
            text = file.read()
            file.close()

            self.encrypt(image_path, text.strip(), Fernet.generate_key().decode(), balance)

        elif action == 'decrypt':
            try:
                self.decrypt(image_path, key)

            except IndexError:
                self.error("Invalid key.")

            except ValueError:
                self.error("Invalid key.")

        print('')

    def find_max_index(self, array):
        max_num = array[0]
        index = 0
        for i, val in enumerate(array):
            if val > max_num:
                max_num = val
                index = i
        return index

    def balance_channel(self, colors, pix):
        max_color = self.find_max_index(colors)
        colors[max_color] = int(self.last_replace(bin(colors[max_color]), pix), 2)
        while True:
            max_sec = self.find_max_index(colors)
            if max_sec != max_color:
                colors[max_sec] = colors[max_color] - 1
            else:
                break
        return colors

    def encrypt(self, path_to_image, text, key, balance):
        img = dict()
        size = dict()
        coord = dict()
        img["image"] = Image.open(path_to_image)
        img["draw"] = ImageDraw.Draw(img["image"])
        img["pix"] = img["image"].load()
        size["width"] = img["image"].size[0]
        size["height"] = img["image"].size[1]
        text = self.des_encrypt(text, key)
        binary_text = self.text_to_binary(text)
        list_two = self.split_count(''.join(binary_text), balance)
        coord["x"] = 0
        coord["y"] = 0
        count = 0
        for i in list_two:
            red, green, blue = img["pix"][coord["x"], coord["y"]]
            (red, green, blue) = self.balance_channel([red, green, blue], i)
            img["draw"].point((coord["x"], coord["y"]), (red, green, blue))
            if coord["x"] < (size["width"] - 1):
                coord["x"] += 1
            elif coord["y"] < (size["height"] - 1):
                coord["y"] += 1
                coord["x"] = 0
            else:
                self.error("Message too long for this image.", True)
            count += 1
        img["image"].save("data/photo/output_photo/out.png", "PNG")
        file = open("data/key/key.dat", "w")
        file.write(str(balance) + '$' + str(count) + '$' + key)
        file.close()
        self.success(str(count) + " pixels takes")
        self.success("Image saved in out.png")
        self.success("Key saved in key.dat")

    def decrypt(self, path_to_image, key):
        balance = int(key.split('$')[0])
        count = int(key.split('$')[1])
        end_key = key.split('$')[2]
        img = dict()
        coord = dict()
        img["image"] = Image.open(path_to_image)
        img["width"] = img["image"].size[0]
        img["height"] = img["image"].size[1]
        img["pix"] = img["image"].load()
        coord["x"] = 0
        coord["y"] = 0
        code = ''
        i = 0
        while i < count:
            pixels = img["pix"][coord["x"], coord["y"]]
            pixel = str(bin(max(pixels)))
            if balance == 4:
                code += pixel[-4] + pixel[-3] + pixel[-2] + pixel[-1]
            elif balance == 3:
                code += pixel[-3] + pixel[-2] + pixel[-1]
            elif balance == 2:
                code += pixel[-2] + pixel[-1]
            else:
                code += pixel[-1]
            if coord["x"] < (img["width"] - 1):
                coord["x"] += 1
            else:
                coord["y"] += 1
                coord["x"] = 0
            i += 1
        outed = self.binary_to_text(self.split_count(code, 8))
        file = open("data/message/output_data/out.txt", "w")
        file.write(self.des_decrypt(''.join(outed), end_key))
        file.close()
        self.success("Data saved in out.txt")

    def des_encrypt(self, text, key):
        cipher = Fernet(key.encode())
        result = cipher.encrypt(text.encode())
        return result.decode()

    def des_decrypt(self, text, key):
        cipher = Fernet(key.encode())
        result = cipher.decrypt(text.encode())
        return result.decode()

    def split_count(self, text, count):
        result = list()
        txt = ''
        var = 0
        for i in text:
            if var == count:
                result.append(txt)
                txt = ''
                var = 0
            txt += i
            var += 1
        result.append(txt)
        return result

    def last_replace(self, main_string, last_symbols):
        return str(main_string)[:-len(last_symbols)] + last_symbols

    def text_to_binary(self, event):
        return ['0' * (8 - len(format(ord(elem), 'b'))) + format(ord(elem), 'b') for elem in event]

    def binary_to_text(self, event):
        return [chr(int(str(elem), 2)) for elem in event]

    def isset(self, array, key):
        try:
            if type(array) is list:
                array[key]
            elif type(array) is dict:
                return key in array.keys()
            return True
        except:
            return False

    def error(self, text, quit=False):
        print(Style.BRIGHT + Fore.YELLOW + "     " + text + Style.RESET_ALL)
        if quit:
            sys.exit()

    def using(self, text, quit=False):
        print(Style.BRIGHT + Fore.WHITE + "     " + text + Style.RESET_ALL)
        if quit:
            sys.exit()

    def success(self, text):
        print(Style.BRIGHT + Fore.GREEN + "     " + text + Style.RESET_ALL)

if __name__ == "__main__":
    LCD = LCD()

    with open('data/message/input_data/hidden_message.txt', 'r') as file:
        text = file.read()
        print("Входящее сообщение: " + text)

    LCD.process_action("encrypt", "data/photo/input_photo/in.jpg", data_path="data/message/input_data/hidden_message.txt", balance=1)

    with open('data/key/key.dat', 'r') as file:
        key = file.read().strip()
    LCD.process_action("decrypt", "data/photo/output_photo/out.png", key=key)

    with open('data/message/output_data/out.txt', 'r') as file:
        key = file.read().strip()
        print("Разшифрованное сообщение: " + key)
