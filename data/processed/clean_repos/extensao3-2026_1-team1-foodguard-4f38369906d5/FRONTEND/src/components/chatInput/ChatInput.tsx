import { FiSend, FiX } from 'react-icons/fi'
import { useRef, useState } from "react";
import { LuScanBarcode } from 'react-icons/lu'
import { Loader2 } from "lucide-react";
import { useBarcode } from "@/hooks/use-barcode";
import { useOpenFood } from "@/hooks/use-open-food";
import type { IOpenFoodProduct } from "@/models/open-food.model";

type ChatInputProps = {
  onSend: (text: string, image?: File, product?: IOpenFoodProduct) => void;
  disabled?: boolean;
};

const ChatInput = ({ onSend, disabled }: ChatInputProps) => {
  const [value, setValue] = useState("");
  const [image, setImage] = useState<File | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const [isScanning, setIsScanning] = useState(false);
  const [scanFailed, setScanFailed] = useState(false);
  const { decodeBarcodeFromFile } = useBarcode();
  const { fetchProduct, productData, isLoading: isProductLoading, isError, error, reset: resetProduct } = useOpenFood();

  const isBusy = disabled || isScanning || isProductLoading;

  const handleSubmit = (e: React.FormEvent<HTMLFormElement> | React.KeyboardEvent<HTMLTextAreaElement>) => {
    e.preventDefault();
    if (isBusy || (!value.trim() && !image)) return;

    onSend(value, image || undefined, productData || undefined);
    setValue('');
    removeImage();

    if (textareaRef.current) {
      textareaRef.current.value = '';
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setValue(e.target.value);
    const textarea = e.target;
    textarea.style.height = 'auto';
    textarea.style.height = `${textarea.scrollHeight}px`;
  }

  const handleImageChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setImage(file);
      setPreviewUrl(URL.createObjectURL(file));// Cria uma URL temporária para o preview

      setIsScanning(true);
      setScanFailed(false);
      resetProduct();

      try {
        const barcode = await decodeBarcodeFromFile(file);
        if (barcode) {
          await fetchProduct(barcode);
        } else {
          // Nenhum código de barras encontrado na imagem (B012).
          setScanFailed(true);
        }
      } catch (err) {
        console.error("Erro ao tentar ler o código de barras", err);
        setScanFailed(true);
      } finally {
        setIsScanning(false);
      }
    }
  }

  const removeImage = () => {
    setImage(null);
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
      setPreviewUrl(null);
    }
    if (fileRef.current) fileRef.current.value = '';
    setScanFailed(false);
    resetProduct();
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter') {
      if (e.shiftKey) {
        return;
      } else {
        e.preventDefault();
        handleSubmit(e);
      }
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col w-full bg-white border border-zinc-500 rounded-3xl transition-all duration-200">

      {previewUrl && (
        <div className="relative p-3 pb-0 flex flex-col gap-3">
          <div className="relative inline-block w-fit">
            <img src={previewUrl} alt="Preview" className="h-20 w-20 object-cover rounded-xl border border-foodguard-300" />
            <button
              type="button"
              onClick={removeImage}
              className="absolute -top-1 -right-1 bg-red-500 text-white rounded-full p-1 shadow-md hover:bg-red-600"
            >
              <FiX className="text-xs" />
            </button>
          </div>

          {(isScanning || isProductLoading) && (
            <div className="flex items-center gap-2 text-sm text-foodguard-600 font-medium animate-pulse px-1">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Analisando imagem em busca de produtos...</span>
            </div>
          )}

          {productData && !isProductLoading && (
            <div className="flex items-center gap-3 p-2 bg-slate-100 rounded-xl border border-zinc-300 w-full max-w-sm shadow-sm animate-fade-in">
              {productData.product.image_front_url ? (
                <img src={productData.product.image_front_url} alt="Produto" className="h-12 w-12 rounded-lg object-cover bg-white" />
              ) : (
                <div className="h-12 w-12 rounded-lg bg-zinc-200 flex items-center justify-center">
                  <LuScanBarcode className="text-red-500" />
                </div>
              )}
              <div className="flex flex-col overflow-hidden">
                <span className="text-sm font-bold text-black truncate">
                  {productData.product.product_name || "Produto sem nome"}
                </span>
                <span className="text-xs text-slate-600 truncate">
                  {productData.product.brands || "Marca não informada"}
                </span>
              </div>
            </div>
          )}

          {isError && !isScanning && !isProductLoading && (
            <div className="text-xs font-medium text-red-500 px-1">
              {error || "Código de barras detectado, mas produto não encontrado."}
            </div>
          )}

          {scanFailed && !isScanning && !isProductLoading && (
            <div className="text-xs font-medium text-amber-600 px-1">
              Não identificamos um código de barras nesta imagem. Você ainda pode
              descrever o produto na mensagem e enviar.
            </div>
          )}
        </div>
      )}

      <div className="flex flex-row items-end gap-2 w-full min-h-11 py-1 px-1">
        <input
          type="file"
          accept="image/*"
          capture="environment"
          ref={fileRef}
          onChange={handleImageChange}
          className="hidden"
        />

        <button
          type="button"
          onClick={() => fileRef.current?.click()}
          aria-label="Escanear código de barras"
          className="flex items-center justify-center bg-transparent p-2 cursor-pointer rounded-full transition-all"
        >
          <LuScanBarcode className="text-2xl text-black" />
        </button>

        <textarea
          ref={textareaRef}
          value={value}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          disabled={isBusy}
          rows={1}
          maxLength={5000}
          className="resize-none w-full max-h-[120px] outline-none py-2.5 bg-transparent text-black overflow-y-auto leading-tight custom-scrollbar placeholder-slate-800/60 placeholder-opacity-80 disabled:bg-transparent disabled:opacity-50 transition-opacity"
          placeholder="O que vamos comer hoje?"
        />

        <button
          type="submit"
          disabled={isBusy}
          aria-label="Enviar"
          className="flex items-center justify-center rounded-full p-2 bg-foodguard-500/20 disabled:opacity-50 transition-all">
          {isBusy && !disabled ? (
            <Loader2 className="text-2xl text-foodguard-500 animate-spin" />
          ) : (
            <FiSend className="text-2xl text-foodguard-500" />
          )}
        </button>
      </div>
    </form>
  );
};

export default ChatInput;
