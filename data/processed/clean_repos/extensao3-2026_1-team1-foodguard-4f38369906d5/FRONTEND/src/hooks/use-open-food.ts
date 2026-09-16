import { useState, useCallback } from "react";
import { openFoodService } from "@/services/open-food.service";
import type { IOpenFoodProduct } from "@/models/open-food.model";

type UseOpenFoodReturn = {
    productData: IOpenFoodProduct | null;
    isLoading: boolean;
    isError: boolean;
    error: string | null;
    fetchProduct: (barcode: string) => Promise<IOpenFoodProduct | null>;
    reset: () => void;
};

const fields = [
    "product_name",
    "brands",
    "categories",
    "image_url",
    "image_front_url",
    "nutriscore_data",
    "nutriscore_grade",
    "nutrition_grades",
    "ingredients",
    "ingredients_text",
    "nutriments",
    "quantity",
    "serving_size",
];

export const useOpenFood = (): UseOpenFoodReturn => {
    const [productData, setProductData] = useState<IOpenFoodProduct | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [isError, setIsError] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const fetchProduct = useCallback(async (barcode: string): Promise<IOpenFoodProduct | null> => {
        if (!barcode) {
            setError("Código de barras não fornecido");
            setIsError(true);
            return null;
        }

        setIsLoading(true);
        setIsError(false);
        setError(null);

        try {
            const data = await openFoodService.getProduct({ barcode, fields });

            if (data.status === 0) {
                setError("Produto não encontrado");
                setIsError(true);
                setProductData(null);
                return null;
            }

            setProductData(data);
            return data;
        } catch (err) {
            console.error("Erro ao buscar produto:", err);
            setError("Falha ao buscar informações do produto");
            setIsError(true);
            setProductData(null);
            return null;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const reset = useCallback(() => {
        setProductData(null);
        setIsLoading(false);
        setIsError(false);
        setError(null);
    }, []);

    return { productData, isLoading, isError, error, fetchProduct, reset };
};

export default useOpenFood;
