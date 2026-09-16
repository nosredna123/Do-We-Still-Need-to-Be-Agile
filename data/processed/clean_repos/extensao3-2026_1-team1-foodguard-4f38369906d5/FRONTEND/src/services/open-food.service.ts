import { openFoodRest } from "./rest/open-food.rest";
import type { IOpenFoodProduct } from "@/models/open-food.model";

const DEFAULT_FIELDS = [
    "product_name", "brands", "categories", "image_url", "image_front_url",
    "nutriscore_data", "nutriscore_grade", "nutrition_grades", "ingredients",
    "ingredients_text", "nutriments", "quantity", "serving_size",
    "allergens_tags", "additives_tags"
].join(",");

type OpenFoodPayload = {
    barcode: string;
    fields?: string[];
};

export const openFoodService = {
    getProduct: async (payload: OpenFoodPayload): Promise<IOpenFoodProduct> => {
        const fieldsString = payload.fields?.join(",") || DEFAULT_FIELDS;

        return await openFoodRest.getProduct(payload.barcode, {
            fields: fieldsString
        });
    }
};
