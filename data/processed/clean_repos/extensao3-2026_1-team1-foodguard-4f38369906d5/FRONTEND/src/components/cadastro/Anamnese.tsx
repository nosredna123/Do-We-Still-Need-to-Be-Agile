import { useState } from "react";
import type { AnamneseRequest, EatingStyle } from "@/models/anamnese.model";
import Radio from "@/components/ui/Radio";
import InfoTooltip from "@/components/ui/InfoTooltip";
import { useToast } from "@/hooks/use-toast";
import { cn } from "@/lib/utils";
import {
  buildAnamnesePayload,
  textareaClass,
  fieldErrorClass,
  validateAnamnese,
} from "@/lib/anamnese.constants";

interface Props {
  onSubmit: (data: AnamneseRequest) => Promise<void>;
  submitting?: boolean;
  error?: string | null;
}

/** Marcador visual de campo obrigatório (C-02). */
const Required = () => (
  <span className="text-red-600" aria-hidden="true"> *</span>
);

/** Mapa chave-do-campo → id do elemento, para focar o campo inválido. */
const FIELD_IDS: Record<string, string> = {
  objetivo: "anamnese-objetivo",
  alergia: "anamnese-alergia",
  intolerancia: "anamnese-intolerancia",
  doencas: "anamnese-doencas",
  medicamentos: "anamnese-medicamentos",
  pref: "anamnese-pref",
  naoGosta: "anamnese-nao-gosta",
};

const AnamneseStep = ({ onSubmit, submitting = false, error }: Props) => {
  const [consulta, setConsulta] = useState("nao");
  const [objetivo, setObjetivo] = useState("");
  const [resultado, setResultado] = useState("");
  const [intolerancia, setIntolerancia] = useState("");
  const [doencas, setDoencas] = useState("");
  const [medicamentos, setMedicamentos] = useState("");
  const [alergia, setAlergia] = useState("");
  const [pref, setPref] = useState("");
  const [naoGosta, setNaoGosta] = useState("");
  const [sentimento, setSentimento] = useState("indiferente");
  const [veg, setVeg] = useState<EatingStyle>("not");
  const [alcool, setAlcool] = useState("nao");
  const [fumo, setFumo] = useState("nao");
  const [localError, setLocalError] = useState<string | null>(null);
  const [errorField, setErrorField] = useState<string | null>(null);
  const { toast } = useToast();

  // onChange que limpa o realce de erro do próprio campo ao ser editado.
  const fieldProps = (key: string, setter: (v: string) => void) => ({
    onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      setter(e.target.value);
      if (errorField === key) setErrorField(null);
    },
    "aria-invalid": errorField === key || undefined,
    className: cn(textareaClass, errorField === key && fieldErrorClass),
  });

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLocalError(null);

    const validationError = validateAnamnese({
      consulta,
      objetivo,
      alergia,
      intolerancia,
      doencas,
      medicamentos,
      pref,
      naoGosta,
    });
    if (validationError) {
      setErrorField(validationError.field);
      setLocalError(validationError.message);
      toast({ variant: "error", description: validationError.message });
      document.getElementById(FIELD_IDS[validationError.field])?.focus();
      return;
    }
    setErrorField(null);

    const payload = buildAnamnesePayload({
      consulta,
      objetivo,
      resultado,
      doencas,
      medicamentos,
      alergia,
      intolerancia,
      pref,
      naoGosta,
      sentimento,
      veg,
      alcool,
      fumo,
    });

    await onSubmit(payload);
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="flex items-center gap-3">
        <h2 className="font-sansita text-2xl font-extrabold tracking-tight text-black sm:text-3xl">
          FORMULÁRIO DE SAÚDE
        </h2>
        <InfoTooltip label="O que é o Formulário de Saúde?">
          O Formulário de Saúde (anamnese) reúne seu histórico alimentar e de
          saúde — alergias, intolerâncias, doenças, medicamentos e preferências.
          O FoodGuard usa esses dados para personalizar a análise de segurança
          dos alimentos que você consome. Quanto mais completo, mais precisas
          são as recomendações.
        </InfoTooltip>
      </div>

      {(localError || error) && (
        <div className="mt-4 rounded-md bg-red-100 px-4 py-2 text-sm font-medium text-red-700">
          {localError || error}
        </div>
      )}

      <p className="mt-4 text-xs text-gray-700">
        Campos marcados com <span className="text-red-600">*</span> são obrigatórios.
      </p>

      <div className="mt-8 grid gap-8 sm:grid-cols-2">
        <div className="space-y-3">
          <p className="font-semibold text-black">
            Já fez consulta prévia com nutricionista?
          </p>
          <div className="space-y-2">
            <Radio
              name="consulta"
              value="sim"
              checked={consulta === "sim"}
              onChange={setConsulta}
              label="Sim"
            />
            <Radio
              name="consulta"
              value="nao"
              checked={consulta === "nao"}
              onChange={setConsulta}
              label="Não"
            />
          </div>
        </div>

        {consulta === "sim" ? (
          <>
            <div className="space-y-2">
              <label
                htmlFor="anamnese-objetivo"
                className="block font-semibold text-black"
              >
                Qual era o objetivo na época?<Required />
              </label>
              <textarea
                id="anamnese-objetivo"
                value={objetivo}
                rows={4}
                aria-required="true"
                {...fieldProps("objetivo", setObjetivo)}
              />
            </div>
            <div className="space-y-2">
              <label
                htmlFor="anamnese-resultado"
                className="block font-semibold text-black"
              >
                Obteve resultado? Se sim, qual?
              </label>
              <textarea
                id="anamnese-resultado"
                value={resultado}
                onChange={(e) => setResultado(e.target.value)}
                rows={4}
                className={textareaClass}
              />
            </div>
          </>
        ) : null}

        <div className="space-y-2">
          <label
            htmlFor="anamnese-intolerancia"
            className="block font-semibold text-black"
          >
            Tem intolerância a algum alimento? Se sim, qual?<Required />
          </label>
          <textarea
            id="anamnese-intolerancia"
            value={intolerancia}
            rows={4}
            aria-required="true"
            {...fieldProps("intolerancia", setIntolerancia)}
          />
        </div>

        <div className="space-y-2">
          <label
            htmlFor="anamnese-alergia"
            className="block font-semibold text-black"
          >
            Possui alergia a algum alimento? Se sim, qual?<Required />
          </label>
          <textarea
            id="anamnese-alergia"
            value={alergia}
            rows={4}
            aria-required="true"
            {...fieldProps("alergia", setAlergia)}
          />
        </div>

        <div className="space-y-2">
          <label
            htmlFor="anamnese-doencas"
            className="block font-semibold text-black"
          >
            Você possui histórico de doenças? Se sim, quais?<Required />
          </label>
          <textarea
            id="anamnese-doencas"
            value={doencas}
            rows={4}
            aria-required="true"
            {...fieldProps("doencas", setDoencas)}
          />
        </div>

        <div className="space-y-2">
          <label
            htmlFor="anamnese-medicamentos"
            className="block font-semibold text-black"
          >
            Faz uso de algum medicamento? Se sim, qual?<Required />
          </label>
          <textarea
            id="anamnese-medicamentos"
            value={medicamentos}
            rows={4}
            aria-required="true"
            {...fieldProps("medicamentos", setMedicamentos)}
          />
        </div>

        <div className="space-y-2">
          <label
            htmlFor="anamnese-pref"
            className="block font-semibold text-black"
          >
            Alimentos que você tem preferência?<Required />
          </label>
          <textarea
            id="anamnese-pref"
            value={pref}
            rows={4}
            aria-required="true"
            {...fieldProps("pref", setPref)}
          />
        </div>

        <div className="space-y-2">
          <label
            htmlFor="anamnese-nao-gosta"
            className="block font-semibold text-black"
          >
            Alimentos que você não gosta?<Required />
          </label>
          <textarea
            id="anamnese-nao-gosta"
            value={naoGosta}
            rows={4}
            aria-required="true"
            {...fieldProps("naoGosta", setNaoGosta)}
          />
        </div>

        <div className="space-y-3">
          <p className="font-semibold text-black">
            Sentimento sobre o seu corpo e alimentação?
          </p>
          <div className="grid grid-cols-2 gap-2">
            <Radio
              name="sent"
              value="muito-satisfeito"
              checked={sentimento === "muito-satisfeito"}
              onChange={setSentimento}
              label="Muito Satisfeito"
            />
            <Radio
              name="sent"
              value="satisfeito"
              checked={sentimento === "satisfeito"}
              onChange={setSentimento}
              label="Satisfeito"
            />
            <Radio
              name="sent"
              value="indiferente"
              checked={sentimento === "indiferente"}
              onChange={setSentimento}
              label="Indiferente"
            />
            <Radio
              name="sent"
              value="insatisfeito"
              checked={sentimento === "insatisfeito"}
              onChange={setSentimento}
              label="Insatisfeito"
            />
            <Radio
              name="sent"
              value="muito-insatisfeito"
              checked={sentimento === "muito-insatisfeito"}
              onChange={setSentimento}
              label="Muito Insatisfeito"
            />
          </div>
        </div>

        <div className="space-y-3">
          <p className="font-semibold text-black">Estilo de alimentação</p>
          <div className="grid grid-cols-2 gap-2">
            <Radio
              name="veg"
              value="not"
              checked={veg === "not"}
              onChange={(v) => setVeg(v as EatingStyle)}
              label="Não"
            />
            <Radio
              name="veg"
              value="vegan"
              checked={veg === "vegan"}
              onChange={(v) => setVeg(v as EatingStyle)}
              label="Vegano(a)"
            />
            <Radio
              name="veg"
              value="vegetarian"
              checked={veg === "vegetarian"}
              onChange={(v) => setVeg(v as EatingStyle)}
              label="Vegetariano(a)"
            />
          </div>
        </div>

        <div className="space-y-3">
          <p className="font-semibold text-black">Ingestão de álcool?</p>
          <div className="space-y-2">
            <Radio
              name="alcool"
              value="sim"
              checked={alcool === "sim"}
              onChange={setAlcool}
              label="Sim"
            />
            <Radio
              name="alcool"
              value="nao"
              checked={alcool === "nao"}
              onChange={setAlcool}
              label="Não"
            />
          </div>
        </div>

        <div className="space-y-3">
          <p className="font-semibold text-black">Fumo?</p>
          <div className="space-y-2">
            <Radio
              name="fumo"
              value="sim"
              checked={fumo === "sim"}
              onChange={setFumo}
              label="Sim"
            />
            <Radio
              name="fumo"
              value="nao"
              checked={fumo === "nao"}
              onChange={setFumo}
              label="Não"
            />
          </div>
        </div>
      </div>

      <div className="mt-10 flex items-center justify-end">
        <button
          type="submit"
          disabled={submitting}
          className="h-12 rounded-lg bg-foodguard-600 px-10 font-bold uppercase tracking-wide text-white transition-colors hover:bg-foodguard-600/90 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {submitting ? "Enviando..." : "Continuar"}
        </button>
      </div>
    </form>
  );
};

export default AnamneseStep;
