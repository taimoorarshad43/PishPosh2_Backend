# PishPosh (an e-commerce site)

PishPosh is modeled after other popular e-commerce sites and is meant to show off what I've been learning as a Software Engineering student. Please enjoy and view the hosted version at this URL. This version is updated to have a React frontend.

https://pishposh.onrender.com/

**Future Features**

AI generated descriptions and tagging

Categories and tagging

Better randomized products

## Page Overview


#### Running instructions

Run the following commands and set ups.

Clone the repo into your machine.

```
$ git clone git@github.com:taimoorarshad43/PishPosh.git
```

Additionally, you'll need to set up Mistral and Stripe API accounts to run AI product descriptions and simulate processing payments.

You'll also need a cloud or local relational database to store product information.

The crendentials and API keys for those should be stored in a .env file that the PishPosh application will look for when starting up.
The .env file has the following fields to be filed out. The **SUPABASE_DATABASE_URI** can be any relational database of your choosing as long as it's compatible with SQLAlchemy.

**SUPABASE_DATABASE_URI**

**STRIPE_TEST_API_KEY**

**MISTRAL_API_KEY**

Refer to the below links for documentation on Mistral and Stripe to set up dev accounts and generate API keys

[Mistral Documentation](https://docs.mistral.ai/api/)

[Stripe](https://docs.stripe.com/keys)



After you've cloned the repo, you'll need to set up a virtual environment and install requirements.

You can do that with the following Python module.
```
$ python3 -m venv venv
```
Activate the Python virtual environment and run pip install.
```
$ source venv/bin/activate
```
```
$ pip install -r requirements.txt
```
After installing requirments and setting up your .env file. You can locally run PishPosh with the following command.
```
$ flask run
```

If you want to seed the database with random products, you can do so with the seedfile as so. Within your virtual environment, run the following.
```
$ python3 seedfile.py
```



#### All Pages

All pages will have a navbar that takes the user to the homepage. They will also allow a user to log in and out as well as sign up.
<br></br>

#### Landing Page

This is where the user will land when they first go to the URL.

This page is mapped to the root URL.

This page will have a navbar that lists different categories of products and will also display products based on the category selected.
<br></br>

#### Product Page

The Product page will host a single product listing. It will also list the seller of the product and allow the user to purchase the item.
<br></br>

#### Sign Up Page

The sign up page will be where users can make an account (username and password) to use PishPosh. They'll need to enter at their first name and optionally their last name.
<br></br>

#### Login Page

The login page will allow returning users to login and make purchases or post listings.
<br></br>

#### Cart Page

The cart page will fill up with items the user selected to purchase. This page will update automatically with whatever the user has decided they want to checkout.
<br></br>

#### Checkout Page

Here the user will finalize their purchase and enter payment information.

The payment information will be processed through the Stripe Dev API to simulate an actual transaction.
<br></br>

#### API Page

This page will allow users to make and recieve the results of API calls to the PishPosh API.

This page will make calls to the backend to get the requisite information.
<br></br>



## API Routes

GET /v1/products

**Meaning:** Will get all products and their IDs as well as the userID of the seller

**Response:** {"Products" : [{"productID", "productname", "userID"}, ...]}

**Response Code:** 200

GET /v1/products/<productID>

**Meaning:** Will get one product based on a valid product ID

**Response:** {"Product": {"productID", "productname", "userID"}}

**Response Code:** 200

<br></br>


GET /v1/users

**Meaning:** Will get all usernames, their IDs, and their first and last names (last name optional)

**Response:** {"Users" : [{"userID", "username", "firstname", "lastname"}, ...]}

**Response Code:** 200

GET /v1/users/<userId>

**Meaning:** Will get one user based on a valid user ID and the products they've listed

**Response:** {"User": {"userID", "username", "firstname", "lastname", "products"}}

**Response Code:** 200

<br></br>


GET /v1/tags

**Meaning:** Will get all tags and their IDs

**Response:** {"Tags" : [{"tagID", "tagname"}, ...]}

**Response Code:** 200

GET /v1/tag/<tagID>

**Meaning:** Will get one tag based on a valid tag ID and the product IDs they're attributed to

**Response:** {"Tag": {"tagID", "tagname", "products"}}

**Response Code:** 200

<br></br>


## User Flows

### Buying Flow

![PishPosh User Buying Flow](images/pishposh_buying_flow.png)
<br></br>

### Selling Flow

![PishPosh User Selling Flow](images/pishposh_selling_flow.png)
<br></br>



## Tech Stack

![PishPosh Tech Stack](images/pishposh_techstack.png)
<br></br>

## Dataflow

![PishPosh Dataflow](images/pishposh_data_diagram.png)
<br></br>
