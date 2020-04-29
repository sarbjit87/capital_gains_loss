
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


def test_new_transaction(test_client, init_database, model_access):
    """
    Test new transaction
    """
    with test_client:
        response = test_client.post('/login',
                                    data=dict(email='user2@example.com', password='Password1!'),
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

        #print(response1)
        print(model_access.query.all())
        assert response.status_code == 200
        assert b"Logout" in response.data
        assert b"Login" not in response.data
        assert b"Register" not in response.data
        assert b"ABC_STOCK" in response1.data


def test_new_transaction2(test_client, init_database, test_with_authenticated_user):
    """
    Test new transaction
    """
    response1 = test_client.post('/transaction/new',
                                    data=dict(security_name="ABCD_STOCK",
                                              transaction_date="09/30/2020 09:00 AM",
                                              transaction_type="buy",
                                              quantity=100,
                                              price_per_share=50,
                                              fees=10),
                                    follow_redirects=True)

    response = test_client.get('/home',follow_redirects=True)
    assert b"ABCD_STOCK" in response.data
    assert b"ABC_STOCK" in response.data
