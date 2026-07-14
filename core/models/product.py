"""Source-agnostic product model.

Every marketplace collector normalizes its raw payload into this shape, so the
stage-gate engine never has to know which marketplace the data came from.
"""

from pydantic import BaseModel


class Product(BaseModel):
    marketplace: str
    external_id: int              # WB: nmId
    root_id: int | None = None    # WB: imtId — groups variants, used to fetch reviews
    name: str
    brand: str | None = None
    seller: str | None = None
    price: float | None = None        # final price shown to the buyer, in rubles
    base_price: float | None = None   # pre-discount price, in rubles
    rating: float | None = None
    reviews: int | None = None
    url: str | None = None
