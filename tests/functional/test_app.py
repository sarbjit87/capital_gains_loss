import json

def savejson(data,jsfile):
    with open(jsfile,'w') as fp:
        json.dump(data, fp, sort_keys=True, default=str)

def loadjson(jsfile):
    with open(jsfile) as fp:
        data = json.load(fp)
    return data

def getDataFromModel(model_access):
    result = model_access.query.all()
    data = {}
    for x in result:
        data[x.id] = {}
        data[x.id].update({
            'transaction_date': x.transaction_date,
            'acb': x.acb,
            'acb_change': x.acb_change,
            'gain_loss': x.gain_loss,
            'amount_in_cad': x.amount_in_cad,
            'transaction_type': x.transaction_type,
            'author': x.author.username,
            'security_name': x.security_name
        })
    return data

def test_home_page_get(test_client):
    """
    When home page is visited, it requires user to be logged-in.
    This test ensures that the user is redirected to login page
    """
    response = test_client.get('/home',follow_redirects=True)
    assert response.status_code == 200
    assert b"Sign Up Now" in response.data

def test_home_page_post(test_client):
    """
    Visiting home page with "POST" request should return 405
    """
    response = test_client.post('/')
    assert response.status_code == 405

def test_valid_login_logout(test_client, init_database):
    """
    Testing Login and Logout
    """
    response = test_client.post('/login',
                                data=dict(username="user1", password='Password1!'),
                                follow_redirects=True)
    assert response.status_code == 200


def test_new_transaction1_user1(test_client, init_database, model_access):
    """
    Test new transaction
    """
    with test_client:
        response = test_client.post('/login',
                                    data=dict(email='user1@example.com', password='Password1!'),
                                    follow_redirects=True)

        response1 = test_client.post('/transaction/new',
                                    data=dict(security_name="ABC_STOCK",
                                              transaction_date="09/30/2020 09:00 AM",
                                              transaction_type="buy",
                                              quantity=100,
                                              price_per_share=50,
                                              fees=10),
                                    follow_redirects=True)

        response2 = test_client.get('/logout',follow_redirects=True)
        assert response.status_code == 200
        assert b"Logout" in response.data
        assert b"Login" not in response.data
        assert b"Register" not in response.data
        assert b"ABC_STOCK" in response1.data


def test_new_transaction1_user2(test_client, init_database, test_with_authenticated_user):
    """
    Test new transaction
    """
    response1 = test_client.post('/transaction/new',
                                    data=dict(security_name="ABCD_STOCK",
                                              transaction_date="01/30/2020 09:00 AM",
                                              transaction_type="buy",
                                              quantity=100,
                                              price_per_share=50,
                                              fees=19.99),
                                    follow_redirects=True)

    response = test_client.get('/home',follow_redirects=True)
    assert b"ABCD_STOCK" in response.data
    assert b"ABC_STOCK"  not in response.data

def test_new_transaction2_user2(test_client, init_database, test_with_authenticated_user):
    """
    Test new transaction
    """
    response1 = test_client.post('/transaction/new',
                                    data=dict(security_name="ABCD_STOCK",
                                              transaction_date="02/20/2020 09:00 AM",
                                              transaction_type="sell",
                                              quantity=50,
                                              price_per_share=120,
                                              fees=10),
                                    follow_redirects=True)

    response = test_client.get('/home',follow_redirects=True)
    assert b"ABCD_STOCK" in response.data
    assert b"ABC_STOCK"  not in response.data

def test_new_transaction3_user2(test_client, init_database, test_with_authenticated_user):
    response1 = test_client.post('/transaction/new',
                                    data=dict(security_name="ABCD_STOCK",
                                              transaction_date="03/30/2020 09:00 AM",
                                              transaction_type="buy",
                                              quantity=50,
                                              price_per_share=130,
                                              fees=10),
                                    follow_redirects=True)

    response = test_client.get('/home',follow_redirects=True)
    assert b"ABCD_STOCK" in response.data
    assert b"ABC_STOCK"  not in response.data

def test_new_transaction4_user2(test_client, init_database, test_with_authenticated_user,model_access):
    response1 = test_client.post('/transaction/new',
                                    data=dict(security_name="ABCD_STOCK",
                                              transaction_date="09/30/2020 09:00 AM",
                                              transaction_type="sell",
                                              quantity=40,
                                              price_per_share=90,
                                              fees=10),
                                    follow_redirects=True)

    response = test_client.get('/home',follow_redirects=True)
    data = getDataFromModel(model_access)
    savejson(data,'tests/functional/result1.json')
    golden=loadjson('tests/functional/golden1.json')
    current=loadjson('tests/functional/result1.json')
    assert golden==current
    assert b"ABCD_STOCK" in response.data
    assert b"ABC_STOCK"  not in response.data

def test_file_upload(test_client, init_database, test_with_authenticated_user,model_access):
    with open('tests/functional/export_data.csv', 'rb') as fp:
        rv = test_client.post('/uploadcsv', data=dict(
                               csvfile=(fp, 'export.csv'),
                           ), follow_redirects=True)
    response = test_client.get('/home',follow_redirects=True)
    data = getDataFromModel(model_access)
    savejson(data,'tests/functional/result2.json')
    golden=loadjson('tests/functional/golden2.json')
    current=loadjson('tests/functional/result2.json')
    assert golden==current
    assert b"DEF" in response.data

    response1 = test_client.get('/home',
                                query_string={'symbol': 'DEF'},
                                follow_redirects=True)
    data = getDataFromModel(model_access)
    savejson(data,'tests/functional/result3.json')
    golden=loadjson('tests/functional/golden3.json')
    current=loadjson('tests/functional/result3.json')
    assert b"43.52" in response1.data


def test_exchange_api(test_client,test_with_authenticated_user):
    data = { 'trans_date' : '02/11/2020 09:00 AM'}
    response = test_client.get('/forex',
                           query_string=data,
                           follow_redirects=True)
    assert b"1.3292" in response.data
