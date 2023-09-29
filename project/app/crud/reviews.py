from app.models.orders import Order
from app.models.reviews import NPS_CSI_Review
from app.models.users import User

CSI_FACTORS = {
    1: "location_availability",
    2: "technical_condition",
    3: "rental_price",
    4: "registration_speed",
    5: "interface_simplicity",
    6: "equipment_variety",
    7: "platform_commission",
    8: "equipment_maintenance",
    9: "technical_support",
    10: "equipment_card_creation",
    11: "applications_and_rent_equipment_management",
}

FORM_MAPPING = {"questionOne": "nps"}
for i in range(1, 12):
    FORM_MAPPING[f"questionTwo{i}_importance"] = f"{CSI_FACTORS[i]}_importance"
    FORM_MAPPING[f"questionTwo{i}_satisfaction"] = f"{CSI_FACTORS[i]}_satisfaction"


async def create_nps_csi_review(order: Order, user: User, review: list) -> NPS_CSI_Review:
    answers = {}
    for item in review:
        key, val = item["question"], item["answer"]
        try:
            answers[FORM_MAPPING[key]] = val
        except KeyError:
            pass

    print(answers)

    review = await NPS_CSI_Review.create(order=order, user=user, **answers)
    return review


async def compute_nps() -> float:
    reviews = await NPS_CSI_Review.all().values_list("nps", flat=True)
    if len(reviews) == 0:
        return 0
    n_promoters = len([x for x in reviews if x >= 9])
    n_detractors = len([x for x in reviews if x <= 6])
    nps = round((n_promoters - n_detractors) / len(reviews) * 100, 2)
    return nps


async def compute_csi() -> float:
    from statistics import mean

    reviews = await NPS_CSI_Review.all().values_list(
        *[f"{x}_importance" for x in CSI_FACTORS.values()], *[f"{x}_satisfaction" for x in CSI_FACTORS.values()]
    )
    reviews_means = list(map(mean, zip(*reviews)))
    n = len(CSI_FACTORS)
    csi_values = [reviews_means[i] * reviews_means[i + n] for i in range(n)]
    csi = {key: csi_values[i] for i, key in enumerate(CSI_FACTORS.values())}
    csi["integral"] = mean(csi_values)
    return csi
