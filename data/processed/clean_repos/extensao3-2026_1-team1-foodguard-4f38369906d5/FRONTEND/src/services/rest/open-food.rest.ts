import api from "@/config/api";
import type { IOpenFoodProduct } from "@/models/open-food.model";

const BASE_URL = "/openfood";

export const openFoodRest = {
    /**
     * Busca um produto pelo código de barras
     * @param barcode Código de barras do produto
     * @param params Objeto contendo os fields desejados
     */
    getProduct: (barcode: string, params?: { fields: string }): Promise<IOpenFoodProduct> => {
        // Aceita apenas dígitos para prevenir path traversal na URL.
        if (!/^\d+$/.test(barcode)) {
            return Promise.reject(new Error("Barcode inválido"));
        }
        return api.get(`${barcode}.json`, params, BASE_URL);
    }
};