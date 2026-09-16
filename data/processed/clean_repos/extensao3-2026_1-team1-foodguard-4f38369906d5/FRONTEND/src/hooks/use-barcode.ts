import { useState, useCallback, useEffect, useRef } from "react";
import type { IImageArray } from "@/models/open-food.model";

// A Web API BarcodeDetector ainda não está nos tipos do lib.dom.
interface BarcodeDetectorLike {
  detect(source: ImageBitmapSource): Promise<Array<{ rawValue: string }>>;
}
interface BarcodeDetectorCtor {
  new (options?: { formats?: string[] }): BarcodeDetectorLike;
  getSupportedFormats(): Promise<string[]>;
}

type UseBarcodeReturn = {
  decodeBarcode: (image: IImageArray) => Promise<string | null>;
  decodeBarcodeFromFile: (file: File) => Promise<string | null>;
  isLoading: boolean;
  isError: boolean;
  engine: "native" | "zxing" | null;
};

const SUPPORTED_FORMATS = ["ean_13", "code_128", "ean_8", "upc_a"];

export const useBarcode = (): UseBarcodeReturn => {
  const [isLoading, setIsLoading] = useState(true);
  const [isError, setIsError] = useState(false);
  const [engine, setEngine] = useState<"native" | "zxing" | null>(null);

  const nativeDetectorRef = useRef<BarcodeDetectorLike | null>(null);
  const zxingRef = useRef<typeof import("zxing-wasm/reader") | null>(null);

  useEffect(() => {
    const init = async () => {
      if ("BarcodeDetector" in window) {
        try {
          const BarcodeDetectorAPI = (
            window as unknown as { BarcodeDetector: BarcodeDetectorCtor }
          ).BarcodeDetector;
          const supported = await BarcodeDetectorAPI.getSupportedFormats();
          const hasEan13 = supported.includes("ean_13");

          nativeDetectorRef.current = new BarcodeDetectorAPI({
            formats: SUPPORTED_FORMATS.filter((f: string) =>
              supported.includes(f),
            ),
          });

          if (hasEan13) {
            setEngine("native");
            setIsLoading(false);
            return;
          }
        } catch {
          // BarcodeDetector existe mas falhou - tenta o fallback
        }
      }

      try {
        const zxing = await import("zxing-wasm/reader");
        zxingRef.current = zxing;
        setEngine("zxing");
      } catch (err) {
        console.error("Falha ao carregar zxing-wasm:", err);
        setIsError(true);
      } finally {
        setIsLoading(false);
      }
    };

    init();
  }, []);

  const toImageData = useCallback((image: IImageArray): ImageData => {
    // Constrói sempre uma cópia respaldada por ArrayBuffer (não SharedArrayBuffer),
    // que é o tipo exigido pelo construtor de ImageData.
    const source = image.data instanceof Uint8ClampedArray ? image.data : new Uint8ClampedArray(image.data);
    const array = new Uint8ClampedArray(source.length);
    array.set(source);

    return new ImageData(array, image.w, image.h);
  }, []);

  const decodeNative = useCallback(
    async (image: IImageArray): Promise<string | null> => {
      const detector = nativeDetectorRef.current;
      if (!detector) return null;

      const imageData = toImageData(image);
      const bitmap = await createImageBitmap(imageData);

      try {
        const results = await detector.detect(bitmap);
        if (results.length > 0) return results[0].rawValue;
        return null;
      } finally {
        bitmap.close();
      }
    },
    [toImageData],
  );

  const decodeZxing = useCallback(
    async (image: IImageArray): Promise<string | null> => {
      const zxing = zxingRef.current;
      if (!zxing) return null;

      const imageData = toImageData(image);
      const results = await zxing.readBarcodes(imageData, {
        tryHarder: true,
        formats: ["EAN13", "EAN8", "UPCA", "Code128"],
        maxNumberOfSymbols: 1,
      });

      if (results.length === 0) return null;

      return results[0].text;
    },
    [toImageData],
  );

  const decodeBarcode = useCallback(
    async (image: IImageArray): Promise<string | null> => {
      if (isLoading || isError) return null;

      try {
        if (nativeDetectorRef.current) {
          const nativeResult = await decodeNative(image);
          if (nativeResult) return nativeResult;
        }

        if (zxingRef.current) {
          return await decodeZxing(image);
        }

        return null;
      } catch (err) {
        console.error("Erro na decodificação:", err);
        return null;
      }
    },
    [isLoading, isError, decodeNative, decodeZxing],
  );

  const decodeBarcodeFromFile = useCallback(
    async (file: File): Promise<string | null> => {
      if (zxingRef.current) {
        try {
          const results = await zxingRef.current.readBarcodes(file, {
            tryHarder: true,
            maxNumberOfSymbols: 1,
          });
          if (results.length > 0) return results[0].text;
          return null;
        } catch (e) {
          console.error("Erro no zxing ao ler arquivo:", e);
        }
      }

      // Fallback manual para o BarcodeDetector Nativo
      return new Promise((resolve) => {
        const img = new Image();
        const url = URL.createObjectURL(file);
        img.onload = async () => {
          try {
            const canvas = document.createElement("canvas");
            canvas.width = img.width;
            canvas.height = img.height;
            const ctx = canvas.getContext("2d");
            if (!ctx) {
              resolve(null);
              return;
            }

            ctx.drawImage(img, 0, 0);
            const imageData = ctx.getImageData(0, 0, img.width, img.height);

            const imageArray: IImageArray = {
              data: imageData.data,
              w: imageData.width,
              h: imageData.height,
            };

            const result = await decodeBarcode(imageArray);
            resolve(result);
          } finally {
            URL.revokeObjectURL(url);
          }
        };
        img.onerror = () => {
          URL.revokeObjectURL(url);
          resolve(null);
        };
        img.src = url;
      });
    },
    [decodeBarcode],
  );

  return { decodeBarcode, decodeBarcodeFromFile, isLoading, isError, engine };
};

export default useBarcode;
