type Ingredients = {
  text: string;
  percent_estimated: number;
  percent_max: number;
  percent_min: number;
};

type Nutriments = {
  carbohydrates: number;
  carbohydrates_100g?: number;
  carbohydrates_unit?: string;
  energy?: number;
  energy_kcal?: number;
  energy_kcal_100g?: number;
  fat?: number;
  fat_100g?: number;
  fiber?: number;
  fiber_100g?: number;
  proteins?: number;
  proteins_100g?: number;
  salt?: number;
  salt_100g?: number;
  saturated_fat?: number;
  saturated_fat_100g?: number;
  sodium?: number;
  sodium_100g?: number;
  sugars?: number;
  sugars_100g?: number;
};

type NutriscoreData = {
  energy: number;
  carbohydrates: number;
  grade?: string;
  score?: number;
};

type ProductData = {
  product_name: string;
  brands?: string;
  categories?: string;
  image_url?: string;
  image_front_url?: string;
  ingredients?: Ingredients[];
  ingredients_text?: string;
  nutriments: Nutriments;
  nutriscore_data?: NutriscoreData;
  nutriscore_grade?: string;
  nutrition_grades?: string;
  quantity?: string;
  serving_size?: string;
};

export interface IOpenFoodProduct {
  code: string;
  product: ProductData;
  status: number;
  status_verbose: string;
}

export interface IImageArray {
  data: Uint8ClampedArray | number[];
  w: number;
  h: number;
}
