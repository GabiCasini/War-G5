let jogadorAtual = null;
let faseAtual = null;
let jogadorCorAtual = null;
const LOCALHOST = "http://127.0.0.1:5000";
let iaExecutando = {};

function fetchJogadores() {
  return fetch(LOCALHOST + "/partida/jogadores", { method: "GET" })
    .then((resp) => {
      if (!resp.ok) {
        return resp
          .json()
          .then((errBody) => {
            throw new Error(
              (errBody && (errBody.mensagem || errBody.message)) ||
                `HTTP ${resp.status}`
            );
          })
          .catch(() => {
            throw new Error(`HTTP ${resp.status}`);
          });
      }
      return resp.json();
    })
    .then((data) => {
      // console.log('jogadores', data.jogadores);
      for (let jogador of data.jogadores) {
        // API pode retornar 'ia' (bool) ou 'tipo' (string). Normalizar para 'humano'|'ai'
        let tipo = "humano";
        if (typeof jogador.ia !== "undefined") {
          tipo = jogador.ia ? "ai" : "humano";
        } else if (typeof jogador.tipo !== "undefined") {
          tipo = jogador.tipo;
        }
        adicionarPlayer(jogador.nome, jogador.cor, tipo);
      }
      return data.jogadores;
    })
    .catch((err) => {
      console.error("Erro ao buscar jogadores:", err.message);
      throw err;
    });
}

function fetchTerritorios() {
  return fetch(LOCALHOST + "/partida/territorios", { method: "GET" })
    .then((resp) => {
      if (!resp.ok) {
        return resp
          .json()
          .then((errBody) => {
            throw new Error(
              (errBody && (errBody.mensagem || errBody.message)) ||
                `HTTP ${resp.status}`
            );
          })
          .catch(() => {
            throw new Error(`HTTP ${resp.status}`);
          });
      }
      return resp.json();
    })
    .then((data) => {
      territorios = data.territorios;
      colorirTerritoriosNoMapa();
      desenharExercitosNoMapa();
      return data.territorios;
    })
    .catch((err) => {
      console.error("Erro ao buscar territórios:", err.message);
      throw err;
    });
}

function fetchEstadoAtual() {
  return fetch(LOCALHOST + "/partida/estado_atual", { method: "GET" })
    .then((resp) => {
      if (!resp.ok) {
        return resp
          .json()
          .then((errBody) => {
            throw new Error(
              (errBody && (errBody.mensagem || errBody.message)) ||
                `HTTP ${resp.status}`
            );
          })
          .catch(() => {
            throw new Error(`HTTP ${resp.status}`);
          });
      }
      return resp.json();
    })
    .then((data) => {
      jogadorAtual = data.turno.jogador_cor;
      faseAtual = data.turno.fase;
      let exercitosParaPosicionar = data.exercitos_disponiveis.total;
      let faseAtualStringPrimeiraMaiuscula =
        faseAtual.charAt(0).toUpperCase() + faseAtual.slice(1);
      let corHexJogador = players.find((p) => p.cor === jogadorAtual).corHex;
      atualizarExercitosParaPosicionar(jogadorAtual, exercitosParaPosicionar);
      atualizarHUD(
        data.turno.jogador_nome,
        corHexJogador,
        faseAtualStringPrimeiraMaiuscula
      );
      console.log(data);

      // Se o jogador atual for IA e estivermos na fase de posicionamento, solicitar execução do turno da IA
      try {
        const playerObj = players.find((p) => p.cor === jogadorAtual);
        if (
          playerObj &&
          playerObj.tipo === "ai" &&
          faseAtual === "posicionamento"
        ) {
          // evita chamadas repetidas enquanto a IA está sendo executada
          if (!iaExecutando[jogadorAtual]) {
            iaExecutando[jogadorAtual] = true;
            invokeIaTurnoCompleto(jogadorAtual).finally(() => {
              iaExecutando[jogadorAtual] = false;
            });
          }
        }
      } catch (e) {
        console.warn("Erro ao tentar disparar IA automaticamente:", e);
      }
      return data;
    })
    .catch((err) => {
      console.error("Erro estado atual:", err.message);
      throw err;
    });
}

function invokeIaTurnoCompleto(jogador_cor) {
  // Abre uma conexão SSE para receber eventos da IA em tempo real.
  return new Promise((resolve, reject) => {
    const url = `${LOCALHOST}/ia/stream?jogador_id=${jogador_cor}&acao=turno_completo`;
    console.log("Abrindo stream IA:", url);
    const es = new EventSource(url);

    // marca execução para evitar reentradas
    iaExecutando[jogador_cor] = true;

    es.onmessage = function (evt) {
      try {
        const data = JSON.parse(evt.data);
        // evento final
        if (data.tipo === "turno_finalizado") {
          es.close();
          iaExecutando[jogador_cor] = false;
          // ressincroniza estado final
          fetchJogadores();
          fetchTerritorios();
          fetchEstadoAtual();
          refreshTerritorios();
          resolve(data);
          return;
        }

        if (data.tipo === "erro") {
          es.close();
          iaExecutando[jogador_cor] = false;
          reject(new Error(data.mensagem || "Erro na IA"));
          return;
        }

        // Processar evento em tempo real (sem replay com delays locais)
        try {
          let ev = data;
          let playerObj = players.find((p) => p.cor === jogador_cor) || {
            nome: jogador_cor,
            corHex: "#999",
          };

          // Atualiza a HUD com a fase atual enviada pelo servidor (se houver)
          try {
            if (ev.fase) {
              let faseLabel = "";
              if (ev.fase === "posicionamento") faseLabel = "Posicionamento";
              else if (ev.fase === "ataque") faseLabel = "Ataque";
              else if (ev.fase === "reposicionamento")
                faseLabel = "Reposicionamento";
              if (faseLabel)
                atualizarHUD(playerObj.nome, playerObj.corHex, faseLabel);
            }
          } catch (err) {
            // não bloquear o processamento do evento se atualizarHUD falhar
            console.warn("Falha ao atualizar HUD a partir do evento IA:", err);
          }

          if (ev.tipo === "posicionar") {
            adicionarExercitos(ev.territorio, ev.qtd || 1);
            destacarTerritorio(ev.territorio);
            setTimeout(() => removerDestaqueTerritorio(ev.territorio), 600);
          } else if (ev.tipo === "ataque_inicio") {
            destacarTerritorio(ev.origem);
            destacarTerritorio(ev.alvo);
            setTimeout(() => {
              removerDestaqueTerritorio(ev.origem);
              removerDestaqueTerritorio(ev.alvo);
            }, 600);
          } else if (ev.tipo === "ataque_resultado") {
            const origem = territorios.find((t) => t.nome === ev.origem);
            const alvo = territorios.find((t) => t.nome === ev.alvo);
            if (
              origem &&
              typeof ev.exercitos_restantes_no_inicio === "number"
            ) {
              origem.exercitos = ev.exercitos_restantes_no_inicio;
            }
            if (
              alvo &&
              typeof ev.exercitos_restantes_no_defensor === "number"
            ) {
              alvo.exercitos = ev.exercitos_restantes_no_defensor;
            }
            if (ev.territorio_conquistado && alvo) {
              alvo.cor_jogador = jogador_cor;
            }
            desenharExercitosNoMapa();
            colorirTerritoriosNoMapa();
          } else if (ev.tipo === "reposicionar") {
            const origemR = territorios.find((t) => t.nome === ev.origem);
            const destinoR = territorios.find((t) => t.nome === ev.destino);
            const qtd = Number(ev.qtd) || 0;
            if (origemR && destinoR && qtd > 0) {
              origemR.exercitos = Math.max(0, origemR.exercitos - qtd);
              destinoR.exercitos = (destinoR.exercitos || 0) + qtd;
              desenharExercitosNoMapa();
            }
            destacarTerritorio(ev.origem);
            destacarTerritorio(ev.destino);
            setTimeout(() => {
              removerDestaqueTerritorio(ev.origem);
              removerDestaqueTerritorio(ev.destino);
            }, 600);
          }
        } catch (e) {
          console.warn("Erro ao processar evento SSE da IA:", e);
        }
      } catch (e) {
        console.error("Erro parseando mensagem SSE:", e, evt.data);
      }
    };

    es.onerror = function (err) {
      console.error("EventSource error:", err);
      iaExecutando[jogador_cor] = false;
      try {
        es.close();
      } catch (e) {}
      reject(err);
    };
  });
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function replayIaEvents(events, intervaloMs = 1000, jogadorCor) {
  if (!Array.isArray(events) || events.length === 0) return;
  const playerObj = players.find((p) => p.cor === jogadorCor) || {
    nome: jogadorCor,
    corHex: "#999",
  };

  for (const ev of events) {
    try {
      // atualizar HUD conforme o tipo do evento (mostra a IA em ação)
      let faseLabel = "";
      if (ev.tipo === "posicionar") faseLabel = "Posicionamento";
      else if (ev.tipo === "ataque_inicio" || ev.tipo === "ataque_resultado")
        faseLabel = "Ataque";
      else if (ev.tipo === "reposicionar") faseLabel = "Reposicionamento";
      if (faseLabel) {
        try {
          atualizarHUD(playerObj.nome, playerObj.corHex, faseLabel);
        } catch (err) {
          // se atualizarHUD não existir, ignorar
        }
      }

      switch (ev.tipo) {
        case "posicionar":
          // Atualiza localmente os exércitos para dar feedback visual
          adicionarExercitos(ev.territorio, ev.qtd || 1);
          destacarTerritorio(ev.territorio);
          await sleep(intervaloMs);
          removerDestaqueTerritorio(ev.territorio);
          break;

        case "ataque_inicio":
          // Realça origem e alvo brevemente
          destacarTerritorio(ev.origem);
          destacarTerritorio(ev.alvo);
          await sleep(intervaloMs);
          removerDestaqueTerritorio(ev.origem);
          removerDestaqueTerritorio(ev.alvo);
          break;

        case "ataque_resultado":
          // Atualiza contagens locais quando disponíveis e, se conquistado, ajusta dono
          const origem = territorios.find((t) => t.nome === ev.origem);
          const alvo = territorios.find((t) => t.nome === ev.alvo);
          if (origem && typeof ev.exercitos_restantes_no_inicio === "number") {
            origem.exercitos = ev.exercitos_restantes_no_inicio;
          }
          if (alvo && typeof ev.exercitos_restantes_no_defensor === "number") {
            alvo.exercitos = ev.exercitos_restantes_no_defensor;
          }
          if (ev.territorio_conquistado && alvo) {
            // atacante é o jogadorCor passado para a reprodução
            alvo.cor_jogador = jogadorCor;
          }
          desenharExercitosNoMapa();
          colorirTerritoriosNoMapa();
          await sleep(intervaloMs);
          break;

        case "reposicionar":
          const origemR = territorios.find((t) => t.nome === ev.origem);
          const destinoR = territorios.find((t) => t.nome === ev.destino);
          const qtd = Number(ev.qtd) || 0;
          if (origemR && destinoR && qtd > 0) {
            origemR.exercitos = Math.max(0, origemR.exercitos - qtd);
            destinoR.exercitos = (destinoR.exercitos || 0) + qtd;
            desenharExercitosNoMapa();
          }
          destacarTerritorio(ev.origem);
          destacarTerritorio(ev.destino);
          await sleep(intervaloMs);
          removerDestaqueTerritorio(ev.origem);
          removerDestaqueTerritorio(ev.destino);
          break;

        default:
          // desconhecido: apenas esperar e continuar
          await sleep(intervaloMs);
      }
    } catch (err) {
      console.warn("Erro ao processar evento da IA:", err, ev);
    }
  }
}

function postPassarTurno() {
  return fetch(LOCALHOST + "/partida/finalizar_turno", { method: "POST" })
    .then((resp) => {
      if (!resp.ok) {
        return resp
          .json()
          .then((errBody) => {
            throw new Error(
              (errBody && (errBody.mensagem || errBody.message)) ||
                `HTTP ${resp.status}`
            );
          })
          .catch(() => {
            throw new Error(`HTTP ${resp.status}`);
          });
      }
      return resp.json();
    })
    .then((data) => {
      console.log("Turno finalizado com sucesso:", data);
      fetchJogadores();
      fetchTerritorios();
      fetchEstadoAtual();
      refreshTerritorios();
      return data;
    })
    .catch((err) => {
      console.error("Erro ao finalizar turno:", err.message);
      throw err;
    });
}

function postPosicionarExercitos(jogador_cor, territorio, quantidade) {
  return fetch(LOCALHOST + "/partida/posicionamento", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      jogador_id: jogador_cor,
      territorio: territorio,
      exercitos: quantidade,
    }),
  })
    .then((resp) => {
      if (!resp.ok) {
        return resp
          .json()
          .then((errBody) => {
            throw new Error(
              (errBody && (errBody.mensagem || errBody.message)) ||
                `HTTP ${resp.status}`
            );
          })
          .catch(() => {
            throw new Error(`HTTP ${resp.status}`);
          });
      }
      return resp.json();
    })
    .then((data) => {
      console.log("Exércitos posicionados com sucesso:", data);
      fetchTerritorios();
      fetchEstadoAtual();
      return data;
    })
    .catch((err) => {
      console.error("Erro ao posicionar exércitos:", err.message);
      throw err;
    });
}

function postAtaque(jogador_cor, territorio_origem, territorio_ataque) {
  return fetch(LOCALHOST + "/partida/ataque", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      jogador_id: jogador_cor,
      territorio_origem: territorio_origem,
      territorio_ataque: territorio_ataque,
    }),
  })
    .then((resp) => {
      if (!resp.ok) {
        return resp
          .json()
          .then((errBody) => {
            throw new Error(
              (errBody && (errBody.mensagem || errBody.message)) ||
                `HTTP ${resp.status}`
            );
          })
          .catch(() => {
            throw new Error(`HTTP ${resp.status}`);
          });
      }
      return resp.json();
    })
    .then((data) => {
      console.log("Ataque realizado com sucesso:", data);
      fetchTerritorios();
      fetchEstadoAtual();
      return data;
    })
    .catch((err) => {
      console.error("Erro ao realizar ataque:", err.message);
      throw err;
    });
}

fetchJogadores();
fetchTerritorios();
fetchEstadoAtual();
