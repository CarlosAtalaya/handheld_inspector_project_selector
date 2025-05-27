'''
    writehtml.py module

    Write html file from template and fill fields.

    NOTE: it is essential to save report.html in the path
    'jec25/UI/report/report.html' to ensure all modules, images, and styles are
    imported correctly.
'''
from bs4 import BeautifulSoup

CT_DEFAULT_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
    <link rel="stylesheet" href="../static/css/style.css">
</head>
<body>
    <div class="a4-container">
        <div class="a4-document"></div>
    </div>
</body>
</html>
'''


class WriteHtml():
    def __init__(self,):
        """
        A class for generating HTML reports.

        Usage Example:

        ```python
        DATA = {...}
        IMAGES = {...}

        template_path = 'jec25/UI/static/templates/template.html'
        WH = WriteHtml()

        WH.new_html('Inspection_Report')

        new_template = WH.get_template(template_path)
        WH.set_fill_data(new_template, text_dict=DATA, img_dict=IMAGES)
        WH.add_page(new_template)

        index_template = WH.get_template(template_path)
        WH.add_page(index_template)

        WH.save_html('jec25/UI/reports/report.html')
        ```
        """
        pass

    def new_html(self, title, index_path=None):
        '''
        Create new HTML file.
        Args:
        - title (str): document title.
        - index_path (str, optional): path to base html file.
        '''
        if index_path:
            html_file = self._open_html(index_path)
        else:
            html_file = CT_DEFAULT_HTML

        self._html = self._parse_html(html_file)
        self._set_title(self._html, title)

    def get_template(self, index_path, template_class='a4-page'):
        '''
        Open HTML file, parse its content and return <div> element matching
        the given class in 'template_class'.
        Args:
        - index_path (str): path to HTML template file.
        - template_class (str): class name of the <div> to extract.
        Returns:
        - parsed div.
        '''
        html_file = self._open_html(index_path)
        parsed_html = self._parse_html(html_file)

        div = self.find(parsed_html, template_class, type_='class')
        parsed_div = self._parse_html(str(div)).div  # copy original div
        return parsed_div

    def add_page(self, page, class_='a4-document'):
        '''
        Add new page (HTML content) to the body of the HTML file
        Args:
        - page (bs4 tag): parsed HTML element.
        '''
        div_container = self._html.find(class_=class_)
        # Inserts at top, since print CSS reverses order
        div_container.insert(0, page)

    def find(self, parsed_html, str_key, type_=None):
        '''
        Find and returns first matching HTML element based on the given key.
        Args:
        - parsed_html (bs4 tag): parsed HTML element.
        - str_key (str): key to match in HTML.
        - type_ (str, optional): the type of search to perform.
            - 'id' to search element by ID.
            - 'class' to search element by class name.
            - None (default) to search by tag name.
        Returns:
        - tag (first matching element it found) or None.
        '''
        if type_ == 'id':
            element = parsed_html.find(id=str_key)
        elif type_ == 'class':
            element = parsed_html.find(class_=str_key)
        else:
            element = parsed_html.find(str_key)
        return element

    def find_all(self, parsed_html, str_key, type_=None):
        '''
        Find and returns all matching HTML elements based on the given key.
        Args:
        - parsed_html (bs4 tag): parsed HTML element.
        - str_key (str): key to match in HTML.
        - type_ (str, optional): the type of search to perform.
            - 'id' to search elements by ID.
            - 'class' to search elements by class name.
            - None (default) to search by tag name.
        Returns:
        - list of tags if matching, or empty list.
        '''
        if type_ == 'id':
            elements = parsed_html.find_all(id=str_key)
        elif type_ == 'class':
            elements = parsed_html.find_all(class_=str_key)
        else:
            elements = parsed_html.find_all(str_key)
        return elements

    def set_fill_data(self, parsed_html, text_dict={}, img_dict={}):
        '''
        Fill HTML elements that math the 'fill-*' class.
        Args:
        - parsed_html (bs4 tag): parsed HTML element.
        - text_dict (dict): key-value (class-str_value) pairs.
        - img_dict (dict): key-value (class-img_path) pairs.
        '''
        for key, value in text_dict.items():
            elements = self.find_all(parsed_html, f'fill-{key}', type_='class')
            for element in elements:
                element.string = value

        for key, value in img_dict.items():
            elements = self.find_all(parsed_html, f'fill-{key}', type_='class')
            for element in elements:
                element['src'] = value

    def set_string(self, parsed_html, str_key, str_value, type_=None):
        '''
        Set matching HTML element to str_value, based on given key.
        Args:
        - parsed_html (bs4 tag): parsed HTML element.
        - str_key (str): key to match in HTML.
        - str_value (str): value for element.
        - type_ (str, optional): the type of search to perform.
            - 'id' to search elements by ID.
            - 'class' to search elements by class name.
            - None (default) to search by tag name.
        '''
        elements = self.find_all(parsed_html, str_key, type_)
        for element in elements:
            element.string = str_value

    def set_img(self, parsed_html, str_key, img_path, type_=None):
        '''
        Set matching HTML element to img_path, based on given key.
        Args:
        - parsed_html (bs4 tag): parsed HTML element.
        - str_key (str): key to match in HTML.
        - img_path (str): path to image.
        - type_ (str, optional): the type of search to perform.
            - 'id' to search elements by ID.
            - 'class' to search elements by class name.
            - None (default) to search by tag name.
        '''
        elements = self.find_all(parsed_html, str_key, type_)
        for element in elements:
            element['src'] = img_path

    def save_html(self, path):
        ''' Save HTML file to path. '''
        self._write_html(path)

    def _set_title(self, parsed_html, title):
        ''' Set HTML document title. '''
        self.set_string(parsed_html, 'title', title)

    def _parse_html(self, html_file):
        ''' Parse HTML file '''
        return BeautifulSoup(html_file, 'html.parser')

    def _open_html(self, path):
        ''' Open HTML file. '''
        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()
        return html

    def _write_html(self, path):
        ''' Write HTML file '''
        with open(path, 'w', encoding='utf-8') as f:
            f.write(self._html.prettify())
