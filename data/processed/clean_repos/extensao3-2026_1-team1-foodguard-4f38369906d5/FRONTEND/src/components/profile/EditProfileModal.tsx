import { useCallback, useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { X, User as UserIcon, Database, Pencil, Mail } from "lucide-react";
import logo from "@/assets/logo.svg";
import { useAuth } from "@/hooks/use-auth";
import { useToast } from "@/hooks/use-toast";
import { authService } from "@/services/auth.service";
import { anamneseService } from "@/services/anamnese.service";
import { ANAMNESE_UPDATED_EVENT } from "@/lib/events";
import Radio from "@/components/ui/Radio";
import PasswordField from "@/components/ui/PasswordField";
import {
  FEELING_MAP as FEELING_TO_BACKEND,
  FEELING_TO_FORM,
  PASSWORD_REGEX,
  extractError,
  fieldErrorClass,
  validateAnamnese,
} from "@/lib/anamnese.constants";
import { cn } from "@/lib/utils";
import type {
  Anamnese,
  AnamneseRequest,
  EatingStyle,
} from "@/models/anamnese.model";

interface Props {
  open: boolean;
  onClose: () => void;
}

type Section = "pessoal" | "anamnese";

const FOCUSABLE_SELECTOR =
  'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])';

/** Marcador visual de campo obrigatório (C-02). */
const Required = () => (
  <span className="text-red-600" aria-hidden="true"> *</span>
);

const EditProfileModal = ({ open, onClose }: Props) => {
  const [section, setSection] = useState<Section>("pessoal");
  const dialogRef = useRef<HTMLDivElement>(null);

  // Focus trap + Escape: foca o primeiro elemento ao abrir, mantém o Tab dentro
  // do modal e fecha no Escape (MEDIUM-F10).
  useEffect(() => {
    if (!open) return;

    const dialog = dialogRef.current;
    const focusables =
      dialog?.querySelectorAll<HTMLElement>(FOCUSABLE_SELECTOR);
    focusables?.[0]?.focus();

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose();
        return;
      }
      if (e.key !== "Tab" || !dialog) return;

      const items = dialog.querySelectorAll<HTMLElement>(FOCUSABLE_SELECTOR);
      if (items.length === 0) return;
      const first = items[0];
      const last = items[items.length - 1];

      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [open, onClose]);

  if (!open) return null;

  return createPortal(
    <div
      role="dialog"
      aria-modal="true"
      className="fixed inset-0 z-50 flex items-center justify-center backdrop-blur bg-black/50 p-4 animate-fade-in"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div
        ref={dialogRef}
        className="flex w-full max-w-4xl overflow-hidden rounded-2xl bg-white shadow-2xl"
      >
        <aside className="flex w-56 flex-col gap-2 bg-slate-100 border-r border-zinc-500/50 p-4">
          <button
            onClick={onClose}
            aria-label="Fechar"
            className="mb-4 flex h-9 w-9 items-center justify-center rounded-md text-black hover:bg-slate-200"
          >
            <X className="h-5 w-5" />
          </button>

          <button
            onClick={() => setSection("pessoal")}
            className={`flex items-center gap-3 rounded-lg px-4 py-3 text-left font-semibold transition-colors ${
              section === "pessoal"
                ? "bg-foodguard-500 text-white font-bold"
                : "text-black hover:bg-slate-200"
            }`}
          >
            <UserIcon className="h-5 w-5" />
            Pessoal
          </button>

          <button
            onClick={() => setSection("anamnese")}
            className={`flex items-center gap-3 rounded-lg px-4 py-3 text-left font-semibold transition-colors ${
              section === "anamnese"
                ? "bg-foodguard-500 text-white font-bold"
                : "text-black hover:bg-slate-200"
            }`}
          >
            <Database className="h-5 w-5" />
            Formulário de Saúde
          </button>
        </aside>

        {/* Content */}
        <div className="max-h-[90vh] flex-1 overflow-y-auto p-8">
          {section === "pessoal" ? <PessoalSection /> : <AnamneseSection />}
        </div>
      </div>
    </div>,
    document.body,
  );
};

const EditHeader = ({
  title,
  editing,
  onEdit,
}: {
  title: string;
  editing: boolean;
  onEdit: () => void;
}) => (
  <div className="mb-8 flex items-center gap-4">
    <h2 className="font-sansita text-4xl font-bold tracking-tight text-black">
      {title}
    </h2>
    <button
      onClick={onEdit}
      className={`flex items-center gap-2 rounded-full border-2 border-foodguard-500 px-4 py-1.5 text-sm font-semibold transition-colors ${
        editing
          ? "bg-foodguard-600 text-white font-bold"
          : "text-black hover:bg-foodguard-500/10"
      }`}
    >
      <Pencil className="h-4 w-4" />
      Editar
    </button>
  </div>
);

const fieldClass = (editing: boolean) =>
  `h-11 w-full rounded-md border border-border px-3 pr-10 text-black focus:border-foodguard-500 focus:outline-none focus:ring-2 focus:ring-foodguard-500/30 ${
    editing ? "bg-slate-50" : "bg-slate-100 cursor-not-allowed"
  }`;

const textareaClass = (editing: boolean) =>
  `w-full resize-none rounded-md border border-border px-3 py-2 text-black focus:border-foodguard-500 focus:outline-none focus:ring-2 focus:ring-foodguard-500/30 ${
    editing ? "bg-slate-50" : "bg-slate-100 cursor-not-allowed"
  }`;

const PessoalSection = () => {
  const { user, setUser } = useAuth();
  const { toast } = useToast();
  const [editing, setEditing] = useState(false);

  const [username, setUsername] = useState(user?.username ?? "");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const handleUpdate = async () => {
    setError(null);

    if (password) {
      if (!PASSWORD_REGEX.test(password)) {
        const message =
          "A senha precisa de no mínimo 8 caracteres, com maiúscula, minúscula e número.";
        setError(message);
        toast({ variant: "error", description: message });
        return;
      }
      if (password !== confirm) {
        const message = "As senhas não coincidem.";
        setError(message);
        toast({ variant: "error", description: message });
        return;
      }
    }

    const payload: { username?: string; password?: string } = {};
    if (username && username !== user?.username) payload.username = username;
    if (password) payload.password = password;

    if (Object.keys(payload).length === 0) {
      setEditing(false);
      return;
    }

    setSaving(true);
    try {
      const updated = await authService.atualizarPerfil(payload);
      setUser(updated);
      setPassword("");
      setConfirm("");
      toast({ variant: "success", description: "Perfil atualizado com sucesso." });
      setEditing(false);
    } catch (err) {
      setError(extractError(err, "Não foi possível atualizar o perfil."));
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <EditHeader
        title="DADOS PESSOAIS"
        editing={editing}
        onEdit={() => setEditing((s) => !s)}
      />

      {error && (
        <div className="mb-4 rounded-md bg-red-100 px-4 py-2 text-sm font-medium text-red-700">
          {error}
        </div>
      )}

      <div className="grid gap-8 sm:grid-cols-[1fr_auto] sm:items-start">
        <div className="space-y-6">
          <div className="space-y-2">
            <label htmlFor="perfil-nome" className="block text-sm font-semibold text-black">
              Nome
            </label>
            <div className="relative">
              <input
                id="perfil-nome"
                type="text"
                value={user?.name ?? ""}
                disabled
                className={fieldClass(false)}
              />
              <UserIcon className="pointer-events-none absolute right-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-800" />
            </div>
          </div>

          <div className="space-y-2">
            <label htmlFor="perfil-usuario" className="block text-sm font-semibold text-black">
              Seu usuário
            </label>
            <div className="relative">
              <input
                id="perfil-usuario"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                disabled={!editing}
                className={fieldClass(editing)}
              />
              <UserIcon className="pointer-events-none absolute right-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-800" />
            </div>
          </div>

          <div className="space-y-2">
            <label htmlFor="perfil-email" className="block text-sm font-semibold text-black">
              Seu email
            </label>
            <div className="relative">
              <input
                id="perfil-email"
                type="email"
                value={user?.email ?? ""}
                disabled
                className={fieldClass(false)}
              />
              <Mail className="pointer-events-none absolute right-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-800" />
            </div>
          </div>
        </div>

        <div className="flex justify-center sm:justify-end">
          <img src={logo} alt="" className="h-40 w-40 rounded-full" />
        </div>
      </div>

      <div className="mt-6 grid gap-6 sm:grid-cols-2">
        <PasswordField
          label="Nova senha"
          value={password}
          onChange={setPassword}
          disabled={!editing}
          autoComplete="new-password"
          placeholder={editing ? "Deixe em branco para manter" : "************"}
          inputClassName={fieldClass(editing)}
          showStrength
        />

        <PasswordField
          label="Confirmar a senha"
          value={confirm}
          onChange={setConfirm}
          disabled={!editing}
          autoComplete="new-password"
          placeholder={editing ? "Repita a nova senha" : "************"}
          inputClassName={fieldClass(editing)}
          error={
            confirm.length > 0 && confirm !== password
              ? "As senhas não coincidem."
              : undefined
          }
        />
      </div>

      <div className="mt-10 flex justify-end">
        <button
          onClick={handleUpdate}
          disabled={!editing || saving}
          className="h-12 rounded-lg bg-foodguard-500 px-10 font-bold uppercase tracking-wide text-white transition-colors hover:bg-foodguard-500/90 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {saving ? "Salvando..." : "Atualizar"}
        </button>
      </div>
    </>
  );
};

const ANAMNESE_FIELD_IDS: Record<string, string> = {
  objetivo: "perfil-objetivo",
  alergia: "perfil-alergia",
  intolerancia: "perfil-intolerancia",
  doencas: "perfil-doencas",
  medicamentos: "perfil-medicamentos",
  pref: "perfil-pref",
  naoGosta: "perfil-nao-gosta",
};

const AnamneseSection = () => {
  const { toast } = useToast();
  const [editing, setEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [errorField, setErrorField] = useState<string | null>(null);

  const [consulta, setConsulta] = useState("nao");
  const [objetivo, setObjetivo] = useState("");
  const [resultado, setResultado] = useState("");
  const [alergia, setAlergia] = useState("");
  const [doencas, setDoencas] = useState("");
  const [medicamentos, setMedicamentos] = useState("");
  const [intol, setIntol] = useState("");
  const [pref, setPref] = useState("");
  const [naoGosta, setNaoGosta] = useState("");
  const [sent, setSent] = useState("indiferente");
  const [veg, setVeg] = useState<EatingStyle>("not");
  const [alcool, setAlcool] = useState("nao");
  const [fumo, setFumo] = useState("nao");

  const applyAnamnese = useCallback((a: Anamnese) => {
    setConsulta(a.previous_consultation ? "sim" : "nao");
    setObjetivo(a.previous_consultation_objective ?? "");
    setResultado(a.previous_consultation_result ?? "");
    setAlergia(a.food_allergies ?? "");
    setDoencas(a.disease_history ?? "");
    setMedicamentos(a.medications ?? "");
    setIntol(a.food_intolerances ?? "");
    setPref(a.favorite_foods ?? "");
    setNaoGosta(a.food_aversions ?? "");
    setSent(a.body_feeling ? FEELING_TO_FORM[a.body_feeling] : "indiferente");
    setVeg(a.eating_style);
    setAlcool(a.alcohol_intake ? "sim" : "nao");
    setFumo(a.smoking ? "sim" : "nao");
  }, []);

  // Carrega a anamnese real ao abrir o modal (RF016).
  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);
    anamneseService
      .getMe()
      .then((a) => active && applyAnamnese(a))
      .catch(
        () =>
          active &&
          setError("Não foi possível carregar o formulário de saúde."),
      )
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, [applyAnamnese]);

  const handleUpdate = async () => {
    setError(null);

    const isPrevious = consulta === "sim";

    const validationError = validateAnamnese({
      consulta,
      objetivo,
      alergia,
      intolerancia: intol,
      doencas,
      medicamentos,
      pref,
      naoGosta,
    });
    if (validationError) {
      setErrorField(validationError.field);
      setError(validationError.message);
      toast({ variant: "error", description: validationError.message });
      document
        .getElementById(ANAMNESE_FIELD_IDS[validationError.field])
        ?.focus();
      return;
    }
    setErrorField(null);

    const payload: AnamneseRequest = {
      previous_consultation: isPrevious,
      previous_consultation_objective: isPrevious ? objetivo.trim() : null,
      previous_consultation_result: isPrevious
        ? resultado.trim() || null
        : null,
      disease_history: doencas.trim(),
      medications: medicamentos.trim(),
      food_allergies: alergia.trim(),
      food_intolerances: intol.trim(),
      favorite_foods: pref.trim(),
      food_aversions: naoGosta.trim(),
      body_feeling: FEELING_TO_BACKEND[sent] ?? null,
      eating_style: veg,
      alcohol_intake: alcool === "sim",
      smoking: fumo === "sim",
    };

    setSaving(true);
    try {
      const updated = await anamneseService.atualizar(payload);
      applyAnamnese(updated);
      toast({
        variant: "success",
        description:
          "Formulário de saúde atualizado. Suas conversas serão recarregadas.",
      });
      setEditing(false);
      // RN004: a atualização invalida os chats antigos no backend — sinaliza a UI de chat para recarregar.
      window.dispatchEvent(new Event(ANAMNESE_UPDATED_EVENT));
    } catch (err) {
      setError(
        extractError(err, "Não foi possível atualizar o formulário de saúde."),
      );
    } finally {
      setSaving(false);
    }
  };

  const d = !editing;

  // onChange que limpa o realce de erro do próprio campo ao ser editado.
  const fieldProps = (key: string, setter: (v: string) => void) => ({
    onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      setter(e.target.value);
      if (errorField === key) setErrorField(null);
    },
    "aria-invalid": errorField === key || undefined,
    className: cn(textareaClass(editing), errorField === key && fieldErrorClass),
  });

  return (
    <>
      <EditHeader
        title="FORMULÁRIO DE SAÚDE"
        editing={editing}
        onEdit={() => !loading && setEditing((s) => !s)}
      />

      {error && (
        <div className="mb-4 rounded-md bg-red-100 px-4 py-2 text-sm font-medium text-red-700">
          {error}
        </div>
      )}

      {loading ? (
        <div className="flex h-40 items-center justify-center">
          <span className="animate-pulse text-slate-500">
            Carregando formulário de saúde...
          </span>
        </div>
      ) : (
        <>
          <p className="mb-4 text-xs text-gray-700">
            Campos marcados com <span className="text-red-600">*</span> são obrigatórios.
          </p>
          <div className="grid gap-x-8 gap-y-6 sm:grid-cols-2">
            <div className="space-y-3">
              <p className="text-sm font-semibold text-black">
                Já fez consulta prévia com nutricionista?
              </p>
              <div className="space-y-2">
                <Radio
                  name="consulta"
                  value="sim"
                  checked={consulta === "sim"}
                  onChange={setConsulta}
                  label="Sim"
                  disabled={d}
                />
                <Radio
                  name="consulta"
                  value="nao"
                  checked={consulta === "nao"}
                  onChange={setConsulta}
                  label="Não"
                  disabled={d}
                />
              </div>
            </div>

            {consulta === "sim" ? (
              <>
                <div className="space-y-2">
                  <label htmlFor="perfil-objetivo" className="block text-sm font-semibold text-black">
                    Qual era o objetivo na época?<Required />
                  </label>
                  <textarea
                    id="perfil-objetivo"
                    rows={3}
                    disabled={d}
                    aria-required="true"
                    value={objetivo}
                    {...fieldProps("objetivo", setObjetivo)}
                  />
                </div>

                <div className="space-y-2">
                  <label className="block text-sm font-semibold text-black">
                    Obteve resultado? Se sim, qual?
                  </label>
                  <textarea
                    rows={3}
                    disabled={d}
                    value={resultado}
                    onChange={(e) => setResultado(e.target.value)}
                    className={textareaClass(editing)}
                  />
                </div>
              </>
            ) : null}

            <div className="space-y-2">
              <label htmlFor="perfil-alergia" className="block text-sm font-semibold text-black">
                Possui alergia a algum alimento? Se sim, qual?<Required />
              </label>
              <textarea
                id="perfil-alergia"
                rows={3}
                disabled={d}
                aria-required="true"
                value={alergia}
                {...fieldProps("alergia", setAlergia)}
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="perfil-doencas" className="block text-sm font-semibold text-black">
                Você possui histórico de doenças? Se sim, quais?<Required />
              </label>
              <textarea
                id="perfil-doencas"
                rows={3}
                disabled={d}
                aria-required="true"
                value={doencas}
                {...fieldProps("doencas", setDoencas)}
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="perfil-medicamentos" className="block text-sm font-semibold text-black">
                Faz uso de algum medicamento? Se sim, qual?<Required />
              </label>
              <textarea
                id="perfil-medicamentos"
                rows={3}
                disabled={d}
                aria-required="true"
                value={medicamentos}
                {...fieldProps("medicamentos", setMedicamentos)}
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="perfil-intolerancia" className="block text-sm font-semibold text-black">
                Tem intolerância a algum alimento? Se sim, qual?<Required />
              </label>
              <textarea
                id="perfil-intolerancia"
                rows={3}
                disabled={d}
                aria-required="true"
                value={intol}
                {...fieldProps("intolerancia", setIntol)}
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="perfil-pref" className="block text-sm font-semibold text-black">
                Alimentos que você tem preferência?<Required />
              </label>
              <textarea
                id="perfil-pref"
                rows={3}
                disabled={d}
                aria-required="true"
                value={pref}
                {...fieldProps("pref", setPref)}
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="perfil-nao-gosta" className="block text-sm font-semibold text-black">
                Alimentos que você não gosta?<Required />
              </label>
              <textarea
                id="perfil-nao-gosta"
                rows={3}
                disabled={d}
                aria-required="true"
                value={naoGosta}
                {...fieldProps("naoGosta", setNaoGosta)}
              />
            </div>

            <div className="space-y-3">
              <p className="text-sm font-semibold text-black">
                Sentimento sobre o seu corpo e alimentação?
              </p>
              <div className="grid grid-cols-2 gap-2">
                <Radio
                  name="sent"
                  value="muito-satisfeito"
                  checked={sent === "muito-satisfeito"}
                  onChange={setSent}
                  label="Muito Satisfeito"
                  disabled={d}
                />
                <Radio
                  name="sent"
                  value="satisfeito"
                  checked={sent === "satisfeito"}
                  onChange={setSent}
                  label="Satisfeito"
                  disabled={d}
                />
                <Radio
                  name="sent"
                  value="indiferente"
                  checked={sent === "indiferente"}
                  onChange={setSent}
                  label="Indiferente"
                  disabled={d}
                />
                <Radio
                  name="sent"
                  value="insatisfeito"
                  checked={sent === "insatisfeito"}
                  onChange={setSent}
                  label="Insatisfeito"
                  disabled={d}
                />
                <Radio
                  name="sent"
                  value="muito-insatisfeito"
                  checked={sent === "muito-insatisfeito"}
                  onChange={setSent}
                  label="Muito Insatisfeito"
                  disabled={d}
                />
              </div>
            </div>

            <div className="space-y-3">
              <p className="text-sm font-semibold text-black">
                Estilo de alimentação
              </p>
              <div className="grid grid-cols-2 gap-2">
                <Radio
                  name="veg"
                  value="not"
                  checked={veg === "not"}
                  onChange={(v) => setVeg(v as EatingStyle)}
                  label="Não"
                  disabled={d}
                />
                <Radio
                  name="veg"
                  value="vegan"
                  checked={veg === "vegan"}
                  onChange={(v) => setVeg(v as EatingStyle)}
                  label="Vegano(a)"
                  disabled={d}
                />
                <Radio
                  name="veg"
                  value="vegetarian"
                  checked={veg === "vegetarian"}
                  onChange={(v) => setVeg(v as EatingStyle)}
                  label="Vegetariano(a)"
                  disabled={d}
                />
              </div>
            </div>

            <div className="space-y-3">
              <p className="text-sm font-semibold text-black">
                Ingestão de Álcool?
              </p>
              <div className="space-y-2">
                <Radio
                  name="alcool"
                  value="sim"
                  checked={alcool === "sim"}
                  onChange={setAlcool}
                  label="Sim"
                  disabled={d}
                />
                <Radio
                  name="alcool"
                  value="nao"
                  checked={alcool === "nao"}
                  onChange={setAlcool}
                  label="Não"
                  disabled={d}
                />
              </div>
            </div>

            <div className="space-y-3">
              <p className="text-sm font-semibold text-black">Fumo?</p>
              <div className="space-y-2">
                <Radio
                  name="fumo"
                  value="sim"
                  checked={fumo === "sim"}
                  onChange={setFumo}
                  label="Sim"
                  disabled={d}
                />
                <Radio
                  name="fumo"
                  value="nao"
                  checked={fumo === "nao"}
                  onChange={setFumo}
                  label="Não"
                  disabled={d}
                />
              </div>
            </div>
          </div>

          <div className="mt-10 flex justify-end">
            <button
              onClick={handleUpdate}
              disabled={!editing || saving}
              className="h-12 rounded-lg bg-foodguard-500 px-10 font-bold uppercase tracking-wide text-white transition-colors hover:bg-foodguard-500/90 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {saving ? "Salvando..." : "Atualizar"}
            </button>
          </div>
        </>
      )}
    </>
  );
};

export default EditProfileModal;
