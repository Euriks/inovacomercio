export type FiscalStatus =
  | "CRIADA"
  | "ASSINADA_LOCALMENTE"
  | "PENDENTE_TRANSMISSAO"
  | "TRANSMITIDA"
  | "AUTORIZADA"
  | "REJEITADA"
  | "CANCELADA";

export type FiscalTransaction = {
  vendaId: string;
  numero: number;
  serie: number;
  valorTotal: number;
  chaveAcesso: string;
  modoEmissao: "ONLINE" | "OFFLINE_CONTINGENCIA";
  dhEmi: string;
  dhTransmissao: string | null;
  status: FiscalStatus;
  xml: string;
  qrPayload: string;
  protocolo: string | null;
  idempotente: boolean;
};

const CSC = "DEMO-CSC-SANDBOX";

function mod11(base: string): string {
  const pesos = [2, 3, 4, 5, 6, 7, 8, 9];
  let soma = 0;
  for (let i = 0; i < base.length; i++) {
    soma += Number(base[base.length - 1 - i]) * pesos[i % pesos.length];
  }
  const resto = soma % 11;
  return String(resto === 0 || resto === 1 ? 0 : 11 - resto);
}

export function gerarChave(numero: number, tpEmis: "1" | "9"): string {
  const now = new Date();
  const aamm = `${String(now.getFullYear()).slice(2)}${String(now.getMonth() + 1).padStart(2, "0")}`;
  const cnpj = "14283901000188";
  const cnf = String(Math.floor(Math.random() * 1e8)).padStart(8, "0");
  const base = `50${aamm}${cnpj}65${"001"}${String(numero).padStart(9, "0")}${tpEmis}${cnf}`;
  return base + mod11(base);
}

export function qrPayload(chave: string, modo: string): string {
  return `https://www.fazenda.ms.gov.br/nfce/qrcode?p=${chave}|2|2|000001|${CSC}|modo=${modo}`;
}

export function emitir(params: {
  vendaId: string;
  numero: number;
  serie: number;
  valorTotal: number;
  forceContingencia: boolean;
  existentes: FiscalTransaction[];
}): FiscalTransaction {
  const found = params.existentes.find((n) => n.vendaId === params.vendaId);
  if (found) return { ...found, idempotente: true };

  const offline = params.forceContingencia;
  const chave = gerarChave(params.numero, offline ? "9" : "1");
  const dhEmi = new Date().toISOString();
  const xmlBase = `<?xml version="1.0"?><NFe><nNF>${params.numero}</nNF><chave>${chave}</chave></NFe>`;
  const xml = `${xmlBase}\n<AssinaturaMock certificado_ref="CERT-DEMO-A1-LOJA-01" />`;

  if (offline) {
    return {
      vendaId: params.vendaId,
      numero: params.numero,
      serie: params.serie,
      valorTotal: params.valorTotal,
      chaveAcesso: chave,
      modoEmissao: "OFFLINE_CONTINGENCIA",
      dhEmi,
      dhTransmissao: null,
      status: "PENDENTE_TRANSMISSAO",
      xml,
      qrPayload: qrPayload(chave, "OFFLINE_CONTINGENCIA"),
      protocolo: null,
      idempotente: false,
    };
  }

  return {
    vendaId: params.vendaId,
    numero: params.numero,
    serie: params.serie,
    valorTotal: params.valorTotal,
    chaveAcesso: chave,
    modoEmissao: "ONLINE",
    dhEmi,
    dhTransmissao: dhEmi,
    status: "AUTORIZADA",
    xml,
    qrPayload: qrPayload(chave, "ONLINE"),
    protocolo: `50${dhEmi.slice(2, 10).replace(/-/g, "")}${String(params.numero).padStart(9, "0")}`,
    idempotente: false,
  };
}

export function reconciliar(notas: FiscalTransaction[], online: boolean): FiscalTransaction[] {
  if (!online) return notas;
  return notas.map((n) => {
    if (n.status !== "PENDENTE_TRANSMISSAO" && n.status !== "ASSINADA_LOCALMENTE") return n;
    return {
      ...n,
      status: "AUTORIZADA",
      dhTransmissao: new Date().toISOString(),
      protocolo: n.protocolo || `50${Date.now()}`,
    };
  });
}

export function indicadores(notas: FiscalTransaction[]) {
  return {
    online: notas.filter((n) => n.modoEmissao === "ONLINE").length,
    offline: notas.filter((n) => n.modoEmissao === "OFFLINE_CONTINGENCIA").length,
    pendentes: notas.filter((n) =>
      ["PENDENTE_TRANSMISSAO", "ASSINADA_LOCALMENTE", "CRIADA"].includes(n.status)
    ).length,
    transmitidas: notas.filter((n) => ["TRANSMITIDA", "AUTORIZADA"].includes(n.status)).length,
    autorizadas: notas.filter((n) => n.status === "AUTORIZADA").length,
  };
}
