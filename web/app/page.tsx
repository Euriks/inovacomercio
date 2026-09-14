"use client";

import { QRCodeSVG } from "qrcode.react";
import { useMemo, useState } from "react";
import { emitir, indicadores, reconciliar, type FiscalTransaction } from "../lib/fiscal";

export default function HomePage() {
  const [force, setForce] = useState(true);
  const [vendaId, setVendaId] = useState("V000101");
  const [numero, setNumero] = useState(101);
  const [serie, setSerie] = useState(1);
  const [valor, setValor] = useState(87.42);
  const [fila, setFila] = useState<FiscalTransaction[]>([]);
  const [ultima, setUltima] = useState<FiscalTransaction | null>(null);

  const dash = useMemo(() => indicadores(fila), [fila]);

  function onEmitir() {
    const nota = emitir({
      vendaId,
      numero,
      serie,
      valorTotal: valor,
      forceContingencia: force,
      existentes: fila,
    });
    setUltima(nota);
    if (!nota.idempotente) setFila((prev) => [nota, ...prev]);
  }

  function onReconciliar() {
    setFila((prev) => {
      const next = reconciliar(prev, !force);
      setUltima(next[0] || null);
      return next;
    });
  }

  return (
    <main className="wrap">
      <section className="hero">
        <h1>InovaComércio MS · NFC-e Offline</h1>
        <p>
          Demonstração da camada fiscal em sandbox: emissão online, contingência offline,
          assinatura local, QR Code, fila de transmissão, reconciliação e idempotência —
          compatível com ADR-003, ADR-004 e ADR-005. Sem integração real com SEFAZ.
        </p>
      </section>

      <section className="grid metrics">
        <div className="card"><span>NFC-e Online</span><strong>{dash.online}</strong></div>
        <div className="card"><span>NFC-e Offline</span><strong>{dash.offline}</strong></div>
        <div className="card"><span>Pendentes</span><strong>{dash.pendentes}</strong></div>
        <div className="card"><span>Transmitidas</span><strong>{dash.transmitidas}</strong></div>
        <div className="card"><span>Autorizadas</span><strong>{dash.autorizadas}</strong></div>
      </section>

      <section className="layout">
        <div className="card">
          <h2>Venda → NFC-e</h2>
          <label>
            <input type="checkbox" checked={force} onChange={(e) => setForce(e.target.checked)} />{" "}
            FORCE_CONTINGENCIA (todas as NFC-e entram em contingência)
          </label>
          <label>Venda</label>
          <input value={vendaId} onChange={(e) => setVendaId(e.target.value)} />
          <label>Número</label>
          <input type="number" value={numero} onChange={(e) => setNumero(Number(e.target.value))} />
          <label>Série</label>
          <input type="number" value={serie} onChange={(e) => setSerie(Number(e.target.value))} />
          <label>Valor (R$)</label>
          <input type="number" step="0.01" value={valor} onChange={(e) => setValor(Number(e.target.value))} />
          <button onClick={onEmitir}>Concluir venda</button>
          <button className="secondary" onClick={onReconciliar}>Reconciliar fila</button>
          <p className="flow">
            Venda → detecta indisponibilidade → gera chave → assina XML localmente → QR Code →
            salva XML → fila → venda concluída.
          </p>
        </div>

        <div className="card">
          <h2>Última transação</h2>
          {!ultima && <p className="flow">Nenhuma NFC-e emitida nesta sessão.</p>}
          {ultima && (
            <>
              <p>
                <span className={`badge ${ultima.modoEmissao === "ONLINE" ? "online" : "offline"}`}>
                  {ultima.modoEmissao}
                </span>{" "}
                {ultima.status}
                {ultima.idempotente ? " · idempotente" : ""}
              </p>
              <p className="flow">Chave {ultima.chaveAcesso}</p>
              <div className="qr">
                <QRCodeSVG value={ultima.qrPayload} size={132} />
                <pre className="flow" style={{ whiteSpace: "pre-wrap" }}>{ultima.xml}</pre>
              </div>
            </>
          )}
        </div>
      </section>

      <section className="card" style={{ marginTop: 16 }}>
        <h2>Fila local NFC-e</h2>
        <table>
          <thead>
            <tr>
              <th>Número</th>
              <th>Série</th>
              <th>Data</th>
              <th>Modo</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {fila.length === 0 && (
              <tr><td colSpan={5} className="flow">Fila vazia.</td></tr>
            )}
            {fila.map((n) => (
              <tr key={n.chaveAcesso}>
                <td>{n.numero}</td>
                <td>{n.serie}</td>
                <td>{new Date(n.dhEmi).toLocaleString("pt-BR")}</td>
                <td>{n.modoEmissao}</td>
                <td>{n.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </main>
  );
}
