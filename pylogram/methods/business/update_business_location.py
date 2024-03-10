import pylogram
from pylogram import raw


class UpdateBusinessLocation:
    async def update_business_location(
            self: "pylogram.Client",
            latitude: float | None = None,
            longitude: float | None = None,
            accuracy_radius: int | None = None,
            address: str | None = None
    ) -> bool:
        if latitude is not None and longitude is None:
            raise ValueError("Longitude is required if latitude is provided")

        if longitude is not None and latitude is None:
            raise ValueError("Latitude is required if longitude is provided")

        geo_point = None

        if longitude is not None and latitude is not None:
            geo_point = raw.types.InputGeoPoint(
                lat=latitude,
                long=longitude,
                accuracy_radius=accuracy_radius
            )

        return await self.invoke(
            raw.functions.account.UpdateBusinessLocation(
                geo_point=geo_point,
                address=address
            )
        )
