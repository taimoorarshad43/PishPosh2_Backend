import io
from time import sleep

from flask import Blueprint, session, render_template, redirect, flash, request, jsonify
from PIL import Image
from flask_cors import cross_origin


from models import User, Product, db
from mistraldescription import getproductdescription, encodeimage, decodeimage


uploadroutes = Blueprint("uploadroutes", __name__)

@uploadroutes.route('/upload/<int:userid>', methods = ['POST'])
@cross_origin(supports_credentials=True)
def pictureupload(userid):

    """
    Route to upload a product, need to be logged in to accomplish this.
    """

    if session.get("userid", None) is None:                       # Shouldn't be able to get here from the standard browser.
        print("From /upload route - returned here, userid is: ", session.get("userid", None))
        return jsonify({"error": "Please login to upload products"}), 401
    
    data = request.form                   # Get the data from the request object

    productname = data.get("productName", None)
    productdescription = data.get("productDescription", None)
    productprice = data.get("productPrice", None)
    file = request.files.get('productImage', None)                # Get the file from the request object

    # Declaring an error dict to add and send back errors if any occur
    errors = {
        'productName': '',
        'productDescription': '',
        'productPrice': '',
        'productImage': ''
    }

    if not productname or productname.replace("-","").isdigit() == True:
        errors['productName'] = 'Invalid Product Name'
    if not productdescription or productdescription.replace("-","").isdigit() == True:
        errors['productDescription'] = 'Invalid Product Description'
    if not productprice or int(productprice) <= 0:
        errors['productPrice'] = 'Invalid Product Price'
    if not file:
        errors['productImage'] = 'Missing Image File'

    if any(errors.values()):                  # If any of the errors are not empty, we return the errors to the client
        print("Error values are: ", errors.values())
        return jsonify({"error": errors}), 400

    file_ext = file.filename.split('.')[-1]                # Check if the file is an image and if its in the accepted formats
    print("File ext: ", file_ext)
    if file_ext not in ['jpg', 'jpeg', 'png']:
        errors['file'] = 'Invalid File Type'          # If invalid file type, we'll add an error to session and display it after a redirect
    else:
        if file_ext == 'jpg':
            file_ext = 'jpeg'

    try:                  # Try to commit the product to the database and if not, return errors that might have prevented that
        # Generate new product and attach it to passed userid
        product = Product(productname = productname, productdescription = productdescription, price = productprice, user_id = userid)

        # Resizing and formatting the image into an acceptable format to add to the database
        image = Image.open(file)
        newsize = (200,200)
        image = image.resize(newsize)
        stream = io.BytesIO()
        image.save(stream, format = file_ext.replace('.','').upper())
        file = stream.getvalue()

        # Save the file as base64 encoding to its image filed in DB.
        product.encode_image(file)

        db.session.add(product)
        db.session.commit()

        return jsonify({"success": "Product Listed Successfully"}), 200

    except Exception as e:         # If anything happens during the commit, we send an error JSON back to client
        print(e)
        errors['Misc'] = e
        return jsonify({"error": errors}), 400


@uploadroutes.route('/upload/aiprocess', methods = ['POST'])
@cross_origin(supports_credentials=True)
def aiprocess():

    if session.get("userid", None) is None:                       # Shouldn't be able to get here from the standard browser.
        print("From /upload/ai route - returned here, userid is: ", session.get("userid", None))
        return jsonify({"error": "Please login to upload products"}), 401

    image = request.files['file']
    title_prompt = "Give me a short title for this picture that is 2-5 words long. This title should describe the picture as a product"
    description_prompt = "Give me a product description for this picture that is about 6-12 words long."

    img_data = encodeimage(image)               # Need both an encoded and decoded image for the HTML and API calls respectively
    img_data_decoded = decodeimage(img_data)

    # Temporarily changed to use the encoded image for the API call
    title = getproductdescription(img_data_decoded, title_prompt)     # Get both the title and description from Mistral AI
    sleep(2) # To avoid Mistral API's rate limit
    description = getproductdescription(img_data_decoded, description_prompt)

    output = {"title" : title,
              "description" : description}

    print("From /upload/ai route - output is:", output)

    return jsonify(output)


@uploadroutes.route('/upload/<int:userid>/aiconfirm')
def aiconfirm(userid):

    if session.get("userid", None) is None:
        flash('Please login to upload products', 'btn-info')
        return redirect('/')

    user = User.query.get_or_404(userid)

    img_data_decoded = session.get("aiimage", 1)
    description = session.get("aidesc", 1)
    title = session.get("aititle", 1)

    return render_template('aiconfirm.html', image=img_data_decoded, user=user, title=title, description=description)

##########################################################################################################################################