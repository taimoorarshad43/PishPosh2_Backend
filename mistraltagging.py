import os
from time import sleep

from mistralai.client import MistralClient
from sqlalchemy import func
from app import app

from models import Product, db, Tag
from sqlalchemy.exc import IntegrityError

api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-large-latest"

client = MistralClient(api_key=api_key)

def get_product_tag(desc, prompt=None):

    if prompt is None:

        prompt = f"Give me a list of tags for this product description: {desc}. \
            Please give them in a comma separated list and only 5-10. Do not add any other text.\
                The tags should be more generic and not specific to the product. \
                    only commas and no spaces between the tags."


    chat_response = client.chat.complete(
        model = model,
        messages = [
            {
                "role": "user",
                "content": prompt,
            },
        ]
    )

    # For debugging purposes
    print(chat_response.choices[0].message.content)
    print("-===============================================-")

    output = chat_response.choices[0].message.content

    return output

def get_random_product_description():
    """
    Fetches one random product description from the Product model
    using Flask-SQLAlchemy's `Product.query`.

    This function is used to benchmark the AI model and see how well it performs on random products data.

    :return: A single description string, or None if no products exist.
    """
    random_func = func.random()  # Getting a random number

    with app.app_context():
        result = (
            Product.query
                .with_entities(Product.productname)
                .order_by(random_func)
                .limit(1)
                .first()
        )

    return result[0] if result else None

def testing(sample = 1):
    """
    Test function to get a random product description and generate tags and see how this works
    """
    for x in range(sample):

        desc = get_random_product_description()
        if desc:
            print(f"Random Product Description: {desc}")
            get_product_tag(desc)                           # This function prints the tags
        else:
            print("No product descriptions found.")

        sleep(5)  # Sleep to avoid rate limits


def bulk_tag_all_products():
    """
    Walk through every Product in the database and attach tags.
    """
    with app.app_context():
        # Fetch all products
        all_products = Product.query.all()
        # all_products = Product.query.limit(3)  # For testing

        for product in all_products:
            # Determine which tag-names to attach to this product
            desired_tag_names = get_product_tag(product.productname)
            desired_tag_names = set(desired_tag_names.split(","))
            sleep(5)  # Sleep to avoid rate limits

            print("Desired Tag Names are", desired_tag_names)

            # Fetch existing tag objects for those names in one query
            existing_tags = (
                Tag.query
                .filter(Tag.tagname.in_(desired_tag_names))
                .all()
            )
            existing_names = {t.tagname for t in existing_tags}

            # Create any missing Tag rows
            new_names = desired_tag_names - existing_names
            new_tags = []
            for name in new_names:
                t = Tag(tagname=name)
                db.session.add(t)
                new_tags.append(t)

            # Flush so that new_tags get primary keys
            try:
                db.session.flush()
            except IntegrityError:
                db.session.rollback()
                # In a race condition, another process may have inserted the same tag;
                # let's re-query and continue.
                existing_tags = (
                    Tag.query
                    .filter(Tag.tagname.in_(desired_tag_names))
                    .all()
                )
                new_tags = [t for t in existing_tags if t.tagname in new_names]

            # Combine existing + newly created Tag objects
            all_tag_objs = existing_tags + new_tags

            print("Printing for product", product.productname)
            for tag in all_tag_objs:              # For testing
                print(f"Tag: {tag.tagname}")

            # Assign to product.tags relationship
            product.tags = all_tag_objs

        # Commit everything at once
        db.session.commit()

# bulk_tag_all_products()
# testing(2)