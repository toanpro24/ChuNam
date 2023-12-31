import http.cookies
from http import cookies
from http.server import BaseHTTPRequestHandler
import os
import practice
import urllib.parse
from urllib.parse import parse_qs
from datetime import datetime, timedelta
import datetime
import time
import requests
from http.server import HTTPServer
import smtplib
from email.mime.text import MIMEText
import json
import sqlite3

# Connect to SQL Server

conn = practice.connect_to_database()
cursor = conn.cursor()

class Server(BaseHTTPRequestHandler):
    def do_login(self, username):
     ##-------###
        expiration_date = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        cookie = http.cookies.SimpleCookie()
        cookie['remembered_username'] = username
        cookie['remembered_username']['expires'] = expiration_date.strftime('%a, %d %b %Y %H:%M:%S GMT')
        self.send_response(200)
        self.send_header('Set-Cookie', cookie.output(header=''))
        self.end_headers()
        ##------###

    def do_home_page(self):
        cookie_header = http.cookies.SimpleCookie(self.headers.get('Cookie'))
        if cookie_header:
            cookies = http.cookies.SimpleCookie()
            cookies.load(cookie_header)
            if 'remembered_username' in cookies:
                self.path = '/admin_product_table.html'
                return cookies
        self.path = '/admin.html'

    

    def do_GET(self):
        if ".jpg" in self.path:
            root_path = "C:/Users/phamc/OneDrive/Documents/Chú Nam"
            root_path += self.path
            self.path = root_path

            with open(self.path, 'rb') as f:
                picture_content = f.read()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(picture_content)

        if self.path == '/':
            cookies = self.do_home_page()
            if self.path == '/admin_product_table.html':
                username = cookies['remembered_username'].value
            
        if self.path.startswith("/search"):
            query_string = self.path.split('?', 1)[1]
            query_params = urllib.parse.parse_qs(query_string)
            
            json_data = query_params.get('data')
            if json_data:
                data = json.loads(json_data[0])

            column = data.get('column')
            search_term = data.get('searchTerm')
           
            if column and search_term:
                if "'s" in search_term:
                    index = search_term.find("'s")
                    search_term = search_term[:index] + "'" + search_term[index:]
                if column == 'ProductName':
                    query = f"SELECT * FROM Product WHERE {column} LIKE '%{search_term}%'"
                    cursor.execute(query)
                elif column == 'ProductID':
                    query = f"SELECT * FROM Product WHERE ProductID = {search_term}"
                    cursor.execute(query)
                else:
                    query = f"SELECT * FROM Product Where CategoryID = {search_term}"
                    cursor.execute(query)
                    

                search_results = cursor.fetchall()
                new_html = ""
                for product in search_results:
                    product = list(product)
                    product[1] = "Images/" + product[1]
                    if product[7] == 1:
                        new_html += f'''<tr><td data-column-name = 'ProductID'>{product[0]}</td>
                        <td ><img src="{product[1]}"></td>
                        <td data-column-name = 'ProductName'>{product[2]}</td>
                        <td data-column-name = 'Description'>{product[3]}</td>
                        <td data-column-name = 'Price'>{product[4]}</td>
                        <td data-column-name = 'CategoryID'>{product[5]}</td>
                        <td data-column-name = 'Quantity'>{product[6]}</td>
                        <td><button class="edit-button">Edit</button></td>
                        <td><button class = "delete-button">Delete</button></td>
                        </tr>
                        '''
                with open('admin_product_table.html', 'r') as f:
                    html_content = f.read()
                modified_html_content = html_content.replace('<div id = "product_table"></div>', new_html)
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.wfile.write(modified_html_content.encode('utf-8'))
                return
            else:
                status  = data.get('Status')
                if status != 'All':
                    if status == 'Pending':
                        status = 1
                    elif status == 'Shipped':
                        status = 2
                    else:
                        status = 3
                    cursor.execute(f"SELECT * FROM Orders WHERE Status = {status}")
                    
                else:
                    cursor.execute("SELECT * FROM Orders")
                    
                result = cursor.fetchall()
                order_html = ""
                for order in result:
                    order = list(order)
                    if order[4] == 1:
                        order[4] = 'Pending'
                    elif order[4] == 2:
                        order[4] = 'Shipped'
                    else:
                        order[4] = 'Delivered'
                    order_html += f'''
                    <tr>
                    <td>{order[0]}</td>
                    <td>{order[1]}</td>
                    <td>{order[2]}</td>
                    <td>{order[3]}</td>
                    <td>{order[4]}</td>
                    </tr>
                        '''
                with open('ordersummary.html', 'r') as f:
                    html_content = f.read()
                modified_html_content = html_content.replace('<div id = "ordersummary"></div>', order_html)
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.wfile.write(modified_html_content.encode('utf-8'))
                return
        if self.path == '/ordersummary':
            cursor.execute('SELECT * FROM Orders WHERE STATUS != 3')
            orders = cursor.fetchall()
            order_html = ""
            for order in orders:
                order = list(order)
                if order[4] == 1:
                    order[4] = 'Pending'
                elif order[4] == 2:
                    order[4] = 'Shipped'
                else:
                    order[4] = 'Delivered'
                order_html += f'''
                <tr>
                <td onclick="viewOrderDetails({order[0]})">{order[0]}</td>
                <td onclick="viewOrderDetails({order[0]})">{order[1]}</td>
                <td onclick="viewOrderDetails({order[0]})">{order[2]}</td>
                <td onclick="viewOrderDetails({order[0]})">{order[3]}</td>
                <td>{order[4]}</td>
                <td><button class="edit-button">Edit</button></td>
                </tr>'''
            with open('ordersummary.html', 'r') as f:
                html_content = f.read()
            modified_html_content = html_content.replace('<div id = "ordersummary"></div>', order_html)
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(modified_html_content.encode('utf-8'))
            return
        
        if self.path.startswith('/orderdetails'):
            query_params = self.path.split('?')[1]
            key, value = query_params.split('=')
            if key == 'orderID':
                order_id = value
            cursor.execute(f"SELECT * from OrderDetails where OrderID = {order_id}")
            order_details = cursor.fetchall()
            details_html = ""
            for order_detail in order_details:
                details_html += f'''<tr>
                <td>{order_detail[0]}</td>
                <td>{order_detail[1]}</td>
                <td>{order_detail[2]}</td>
                <td>{order_detail[3]}</td>
                </tr>'''
            with open('orderdetails.html', 'r') as f:
                html_content = f.read()
            modified_html_content = html_content.replace('<div id = "orderdetails"></div>', details_html)
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(modified_html_content.encode('utf-8'))
            return
        if self.path == '/home':
            self.path = '/admin_product_table_redirect.html'
            product_data = practice.Product.read_all()
            product_html = ""
            for product in product_data:
                product = list(product)
                product[1] = "Images/" + product[1]
                if product[7] == 1:
                    product_html += f'''<tr><td data-column-name = 'ProductID'>{product[0]}</td>
                        <td ><img src="{product[1]}"></td>
                        <td data-column-name = 'ProductName'>{product[2]}</td>
                        <td data-column-name = 'Description'>{product[3]}</td>
                        <td data-column-name = 'Price'>{product[4]}</td>
                        <td data-column-name = 'CategoryID'>{product[5]}</td>
                        <td data-column-name = 'Quantity'>{product[6]}</td>
                        <td><button class="edit-button">Edit</button></td>
                        <td><button class = "delete-button">Delete</button></td>
                        </tr>'''
            with open(self.path[1:], 'r') as f:
                html_content = f.read()
            html_content = html_content.replace('<div id = "product_catalog"></div>', product_html)
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers ()
            self.wfile.write(html_content.encode('utf-8'))
            return
        try:
            split_path = os.path.splitext(self.path)
            request_extension = split_path[1]
            if request_extension != ".py":
                if self.path == "/":
                    self.path = "/admin.html"
                with open(self.path[1:], 'r') as f:
                    html_content = f.read()
                self.send_response(200)
                self.end_headers()
                self.wfile.write(bytes(html_content, 'utf-8'))

            else:
                f = "File not found"
                self.send_error(404,f) 
                
        except:
            f = "File not found"
            self.send_error(404,f)


    def do_POST(self):
        
        if self.path == "/updatestatus":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            print(data)
            orderID = data.get('OrderID')
            status  = data.get('Status')
            if status == 'Pending':
                status = 1
            elif status == 'Shipped':
                status = 2
            else:
                status = 3
            practice.Orders.update_status(status, orderID)

        if self.path == "/insert":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            # print(data)
            picture_name = data.get('PictureName')
            product_name = data.get('ProductName')
            description = data.get('Description')
            price = data.get('Price')
            category_id = data.get('CategoryID')
            quantity = data.get('Quantity')
            status = 1
            practice.Product.create(picture_name, product_name, description, price, category_id, quantity, status)
            return
        if self.path == "/update":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            print(data)
            product_id = data.get('ProductID')
            product_name = data.get('ProductName')
            description = data.get('Description')
            price = data.get('Price')
            category_id = data.get('CategoryID')
            quantity = data.get('Quantity')
            status = 1
            practice.Product.update(product_name, description, price, category_id, quantity, product_id, status)
            return
        if self.path == "/delete":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            product_id = data.get('ProductID')
            practice.Product.disable_status(product_id)
            return
        if self.path == "/login":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            post_data = post_data.decode('utf-8')
            form_data = parse_qs(post_data)
            if form_data != {}:
                username = form_data['username'][0]
                password = form_data['password'][0]
            else:
                return
                
            query = "SELECT * FROM Customer WHERE Username = %s AND Password = %s"
            cursor.execute(query, (username, password))
            customer = cursor.fetchone()
            
            if customer:
                #handle log in
                self.do_login(username)
                product_data = practice.Product.read_all()
                product_html = ""
                for product in product_data:
                    product = list(product)
                    product[1] = "Images/" + product[1]

                    if product[7] == 1:
                        product_html += f'''<tr><td data-column-name = 'ProductID'>{product[0]}</td>
                        <td ><img src="{product[1]}"></td>
                        <td data-column-name = 'ProductName'>{product[2]}</td>
                        <td data-column-name = 'Description'>{product[3]}</td>
                        <td data-column-name = 'Price'>{product[4]}</td>
                        <td data-column-name = 'CategoryID'>{product[5]}</td>
                        <td data-column-name = 'Quantity'>{product[6]}</td>
                        <td><button class = "edit-button">Edit</button></td>
                        <td><button class = "delete-button">Delete</button></td>
                        </tr>'''
                    
                with open('admin_product_table.html', 'r') as f:
                    html_content = f.read()
                modified_html_content = html_content.replace('<div id = "product_table"></div>', product_html)
                self.wfile.write(modified_html_content.encode('utf-8'))
                return
            else:
                #not logged in
                self.send_response(401)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                error_message = 'Login failed. Invalid credentials.'
                form_html = '''
                    <form action="/login" method="post">
                        <input class = "username_password"  type="text" name="username" placeholder="Username">
                        <input class = "username_password"  type="password" name="password" placeholder="Password">
                        <input type="submit" value="Login">
                    </form>
                    '''

                response_content = f'<p>{error_message}</p>{form_html}'
                self.wfile.write(bytes(response_content, 'utf-8'))
                return
        

HOST_NAME = 'localhost'
PORT = 8005
#run server
if __name__ == "__main__":
    httpd = HTTPServer((HOST_NAME,PORT),Server)
    print(time.asctime(), "Start Server - %s:%s"%(HOST_NAME,PORT))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print(time.asctime(),'Stop Server - %s:%s' %(HOST_NAME,PORT))   