from bs4 import BeautifulSoup
import json
import re
import requests

global data
data: list = []
def getData(f_data=None):
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'accept-language': 'en-US,en;q=0.7',
        'content-type': 'application/x-www-form-urlencoded',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    }

    if not f_data:
        f_data = {
                'facultyid': 'all',
                'maxrow': '1000',
                'Acadyear': '2566',
                'semester': '1',
                'coursecode': f'004*',
            }
    
    else:
        pass

    response = requests.post('https://reg.msu.ac.th/registrar/class_info_1.asp', headers=headers, data=f_data)

    # check status
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return

    # BeautifulSoup
    resp = BeautifulSoup(response.content, 'html.parser')

    # select table by CSS selector
    soup = resp.select_one('body > div.contenttive > div:nth-child(1) > div.main > div > table:nth-child(6)')


    # Find all rows in the table, excluding the header and footer rows
    rows = soup.find_all('tr', class_='normalDetail')[1:-1]

    # Initialize an empty list to store the JSON data
    # data = []

    # Iterate over each row and extract the required information
    for row in rows:
        cells = row.find_all('td')
        code = cells[1].find('a').text.strip()
        subject_data = cells[2].decode_contents().split("<br/>")
        # TODO: มี font หลุดเข้ามาบางอัน
        name = subject_data[0].split("<font")[0]
        credit = cells[3].text.strip()
        time = cells[4].text.strip()
        sec = int(cells[5].text.strip())
        remain = int(cells[8].text.strip())
        receive = int(cells[6].text.strip())
        # mid = cells[7].text.strip()
        # final = cells[8].text.strip()

        lecturer_raw = subject_data[0]
        try:
            lecturer_raw = subject_data[1]
        except:
            print()
        # Extract the <font> elements within the outer <font> element
        font_elements = re.findall(r'<font[^>]*>.*?</font>', lecturer_raw)
        # Extract the text content of the <li> elements
        li_text = [li for font in font_elements for li in re.findall(r'<li>.*?</li>', font)]
        # Remove the <li> tags from the extracted text
        li_text = [re.findall(r'<li>(.*?)<\/li>', nameLecture)[0].replace('<li>', ' / ') for nameLecture in li_text]
        # Join the extracted text with a delimiter
        lecturer = ' / '.join(li_text)

        # lecturers = lecturer.split(" / ")
        # print(code, lecturers)
        

        # Find the first <font> element
        first_font = re.search(r'<font[^>]*>(.*?)</font>', lecturer_raw)

        # Remove any nested <font> elements within the first <font> element
        content = re.sub(r'<font[^>]*>.*?</font>', '', first_font.group(1))
        # Find the content before the <font> tag
        match = re.search(r'(.*?)<font', content)

        # Extract the content
        if match:
            content = match.group(1)
        else:
            content = ""

        mid = None
        final = None

        try:
            split_data = time.split("สอบปลายภาค")
            mid = split_data[0].strip().split("สอบกลางภาค")[1].strip()
        except:
            print()

        try:
            split_data = time.split("สอบปลายภาค")
            final = split_data[1].strip()
        except:
            print()


        try:
            split_data = time.split("สอบกลางภาค")
            time = split_data[0].strip()
        finally:
            try:
                split_data = time.split("สอบปลายภาค")
                time = split_data[0].strip()
            except:
                print()

        # Define the regular expression pattern
        pattern = r'(\d+)([A-Za-z])'
        # Find all matches in the string
        matches = re.findall(pattern, time)
        # Insert "&" between the number and alphabet character
        time = re.sub(pattern, r'\1 & \2', time)


        type = "GE-"+code[3:4]

        # Create a dictionary for each course and append it to the data list
        course = {
            'type': type,
            'code': code,
            'name': name,
            'note': content,
            'credit': credit,
            'time': time,
            'sec': sec,
            'remain':remain,
            'receive': receive,
            'mid': mid,
            'final': final,
            'lecturer': lecturer
        }
        data.append(course)

    # get nextPages
    try:
        if soup.find_all('tr', class_='normalDetail')[-1].select_one('td:nth-child(2) > a')['href']:
            # get page
            next_f_data = soup.find_all('tr', class_='normalDetail')[-1].select_one('td:nth-child(2) > a')['href'].split('class_info_1.asp?')[1]
            print(next_f_data)
            return getData(next_f_data)
    except Exception:
        print("End")
        pass

    # sort list by remain most
    data.sort(key=lambda x: x['remain'], reverse=True)

    # Save the JSON data to the file
    with open(f"Group/dataALL.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


# split dataALL by Type
def splitData():
    with open(f"Group/dataALL.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    # Create a dictionary for each course and append it to the data list
    GE1 = []
    GE2 = []
    GE3 = []
    GE4 = []
    GE5 = []
    
    for course in data:
        if course['type'] == 'GE-1':
            GE1.append(course)
        elif course['type'] == 'GE-2':
            GE2.append(course)
        elif course['type'] == 'GE-3':
            GE3.append(course)
        elif course['type'] == 'GE-4':
            GE4.append(course)
        elif course['type'] == 'GE-5':
            GE5.append(course)
        
    # Save the JSON data to the file
    for i in range(1,6):
        with open(f"Group/GE-{i}.json", "w", encoding="utf-8") as file:
            json.dump(eval(f"GE{i}"), file, indent=4, ensure_ascii=False)


getData()
splitData()