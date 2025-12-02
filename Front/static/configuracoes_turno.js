let jogadorAtual = null;
let faseAtual = null;
let jogadorCorAtual = null;
const LOCALHOST = "http://127.0.0.1:5000";
let iaExecutando = {};



// Atualiza visibilidade dos controles que devem aparecer apenas para jogadores humanos
function atualizarVisibilidadeBotoes(playerObj) {
  try {
    const wrapper = document.getElementById("passar-turno-wrapper");
    const btnPassar = document.getElementById("btn-passar-turno");
    const btnCartas = document.getElementById("btn-minhas-cartas");

    const isHumano = playerObj && playerObj.tipo === "humano";

    if (wrapper) {
      wrapper.style.display = isHumano ? "flex" : "none";
    } else {
      if (btnPassar)
        btnPassar.style.display = isHumano ? "inline-block" : "none";
      if (btnCartas)
        btnCartas.style.display = isHumano ? "inline-block" : "none";
    }
  } catch (e) {
    console.warn("Falha ao atualizar visibilidade dos botões:", e);
  }
}

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
        adicionarPlayer(jogador.nome, jogador.cor, tipo, tratarObjetivo(jogador.objetivo));
      }
      try {
        if (jogadorAtual) {
          const playerObj = players.find((p) => p.cor === jogadorAtual);
          atualizarVisibilidadeBotoes(playerObj);
        }
      } catch (e) {
        // não bloquear a função principal
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
      // detecta troca de jogador para reiniciar o timer apenas quando necessário
      const jogadorAnterior = jogadorAtual;
      const novoJogador = data.turno.jogador_cor;
      jogadorAtual = novoJogador;
      faseAtual = data.turno.fase;
      let exercitosParaPosicionar = data.exercitos_disponiveis.total;
      tempoTurno = data.turno.tempo_turno;
      let faseAtualStringPrimeiraMaiuscula =
        faseAtual.charAt(0).toUpperCase() + faseAtual.slice(1);
      let corHexJogador = players.find((p) => p.cor === jogadorAtual).corHex;

      players.find((p) => p.cor === jogadorAtual).cartas = data.jogador_cartas.cartas;
      // constroiCartasTroca(data.jogador_cartas.cartas);

      // Se o jogador mudou (início do turno de outro jogador), reinicia o timer
      try {
        if (jogadorAnterior !== novoJogador) {
          if (typeof redefinirTimer === "function") {
            redefinirTimer(tempoTurno);
          } else {
            // fallback: iniciar diretamente (pode ser que redefinirTimer não esteja disponível)
            if (typeof iniciarTimerTurno === "function")
              iniciarTimerTurno(tempoTurno);
          }
        }
      } catch (e) {
        console.warn("Erro ao reiniciar timer na troca de jogador:", e);
      }

      atualizarExercitosParaPosicionar(jogadorAtual, exercitosParaPosicionar);
      atualizarHUD(
        data.turno.jogador_nome,
        corHexJogador,
        faseAtualStringPrimeiraMaiuscula,
        tempoTurno,
        exercitosParaPosicionar
      );
      console.log(data);

      // Se o jogador atual for IA e estivermos na fase de posicionamento, solicitar execução do turno da IA
      try {
        const playerObj = players.find((p) => p.cor === jogadorAtual);
        // Atualiza visibilidade dos botões conforme o tipo do jogador atual
        atualizarVisibilidadeBotoes(playerObj);

        if (
          playerObj &&
          playerObj.tipo === "ai" &&
          faseAtual === "posicionamento"
        ) {
          // evita chamadas repetidas enquanto a IA está sendo executada
          if (!iaExecutando[jogadorAtual]) {
            iaExecutando[jogadorAtual] = true;
            invokeIaTurnoCompleto(
              jogadorAtual,
              tempoTurno,
              exercitosParaPosicionar
            ).finally(() => {
              iaExecutando[jogadorAtual] = false;
            });
          }
        }
      } catch (e) {
        console.warn("Erro ao tentar disparar IA automaticamente:", e);
      }
      atualizaObjetivoPlayer();
      return data;
    })
    .catch((err) => {
      console.error("Erro estado atual:", err.message);
      throw err;
    });
}

function invokeIaTurnoCompleto(
  jogador_cor,
  tempoTurno,
  exercitosParaPosicionar
) {
  // Abre uma conexão SSE para receber eventos da IA em tempo real.
  return new Promise((resolve, reject) => {
    const url = `${LOCALHOST}/ia/stream?jogador_id=${jogador_cor}&acao=turno_completo`;
    console.log("Abrindo stream IA:", url);
    const es = new EventSource(url);

    // marca execução para evitar reentradas
    iaExecutando[jogador_cor] = true;

    // estado local mutável para atualizar HUD dinamicamente durante os eventos SSE
    let restanteExercitos =
      typeof exercitosParaPosicionar === "number"
        ? exercitosParaPosicionar
        : Number(exercitosParaPosicionar) || 0;
    let restanteTempo =
      typeof tempoTurno === "number" ? tempoTurno : Number(tempoTurno) || 0;

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
              if (faseLabel) {
                // atualizar HUD usando os valores locais (restanteTempo/restanteExercitos)
                try {
                  atualizarHUD(
                    playerObj.nome,
                    playerObj.corHex,
                    faseLabel,
                    restanteTempo,
                    restanteExercitos
                  );
                } catch (err) {
                  console.warn(
                    "Falha ao atualizar HUD a partir do evento IA:",
                    err
                  );
                }
              }
            }
          } catch (err) {
            // não bloquear o processamento do evento se atualizarHUD falhar
            console.warn("Falha ao atualizar HUD a partir do evento IA:", err);
          }

          if (ev.tipo === "posicionar") {
            const qtd = Number(ev.qtd) || 1;
            adicionarExercitos(ev.territorio, qtd);
            // atualiza contador local e HUD para refletir exércitos restantes
            restanteExercitos = Math.max(0, restanteExercitos - qtd);
            try {
              atualizarHUD(
                playerObj.nome,
                playerObj.corHex,
                "Posicionamento",
                restanteTempo,
                restanteExercitos
              );
            } catch (err) {
              console.warn(
                "Falha ao atualizar HUD após posicionamento IA:",
                err
              );
            }
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
  return fetch(LOCALHOST + "/partida/avancar_turno", { method: "POST" })
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
      console.log("Turno passado com sucesso:", data);
      fetchJogadores();
      fetchTerritorios();
      fetchEstadoAtual();
      refreshTerritorios();
      return data;
    })
    .catch((err) => {
      console.error("Erro ao passar turno:", err.message);
      throw err;
    });
}

function postFinalizarTurno() {
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
      if (data.status === "finalizado") {
        alert(`Parabéns! ${data.mensagem}`);
        // Só redireciona após o usuário clicar em OK
        window.location.href = "/";
        return data;
      }
      console.log("Exércitos posicionados com sucesso:", data);
      fetchTerritorios();
      fetchEstadoAtual();
      refreshTerritorios();
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
      if (data.status === "finalizado") {
        alert(`Parabéns! ${data.mensagem}`);
        // Só redireciona após o usuário clicar em OK
        window.location.href = "/";
        return data;
      }
      console.log("Ataque realizado com sucesso:", data);

      if (data.rolagens_ataque && data.rolagens_defesa) {
        mostrarResultadoAtaque(data);
      } else {
        alert(
          data.territorio_conquistado
            ? "Território conquistado!"
            : "Ataque finalizado."
        );
        fetchTerritorios();
        fetchEstadoAtual();
      }

      return data;
    })
    .catch((err) => {
      console.error("Erro ao realizar ataque:", err.message);
      alert(`Erro no ataque: ${err.message}`);
      throw err;
    });
}

function postReposicionamento(
  jogador_cor,
  territorio_origem,
  territorio_destino,
  quantidade
) {
  return fetch(LOCALHOST + "/partida/reposicionamento", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      jogador_id: jogador_cor,
      territorio_origem: territorio_origem,
      territorio_destino: territorio_destino,
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
      if (data.status === "finalizado") {
        alert(`Parabéns! ${data.mensagem}`);
        // Só redireciona após o usuário clicar em OK
        window.location.href = "/";
        return data;
      }
      console.log("Reposicionamento realizado com sucesso:", data);
      fetchTerritorios();
      fetchEstadoAtual();
      return data;
    })
    .catch((err) => {
      console.error("Erro ao realizar reposicionamento:", err.message);
      alert(`Erro no reposicionamento: ${err.message}`);
      throw err;
    });
}

function mostrarResultadoAtaque(data) {
  const dialog = document.getElementById("ataqueResultadoDialog");
  const titulo = document.getElementById("ataqueResultadoTitulo");
  const imgsAtaque = document.getElementById("dados-ataque-imgs");
  const imgsDefesa = document.getElementById("dados-defesa-imgs");
  const resultadoTexto = document.getElementById("ataqueResultadoTexto");
  const btnFechar = document.getElementById("ataqueResultadoFechar");

  imgsAtaque.innerHTML = "";
  imgsDefesa.innerHTML = "";

  if (data.rolagens_ataque && Array.isArray(data.rolagens_ataque)) {
    data.rolagens_ataque.forEach((num) => {
      const img = document.createElement("img");
      img.src = `static/d${num}.png`;
      img.alt = `Dado ${num}`;
      imgsAtaque.appendChild(img);
    });
  }

  if (data.rolagens_defesa && Array.isArray(data.rolagens_defesa)) {
    data.rolagens_defesa.forEach((num) => {
      const img = document.createElement("img");
      img.src = `static/d${num}.png`;
      img.alt = `Dado ${num}`;
      imgsDefesa.appendChild(img);
    });
  }

  let mensagem = `Ataque perdeu: ${data.perdas_ataque}. Defesa perdeu: ${data.perdas_defesa}.<br>`;
  if (data.territorio_conquistado) {
    titulo.textContent = "Território Conquistado!";
    mensagem += "<strong>O ataque foi bem-sucedido!</strong>";
  } else {
    titulo.textContent = "Combate Realizado";
    if (data.perdas_ataque > data.perdas_defesa) {
      mensagem += "<strong>A defesa venceu a troca.";
    } else if (data.perdas_defesa > data.perdas_ataque) {
      mensagem += "<strong>O ataque venceu a troca.";
    } else {
      mensagem += "<strong>Houve um empate na troca (defesa vence).";
    }
  }
  resultadoTexto.innerHTML = mensagem;

  btnFechar.onclick = () => {
    dialog.close();
    fetchTerritorios();
    fetchEstadoAtual();
  };

  dialog.showModal();
}

function atualizaObjetivoPlayer() {
  if (faseAtual === 'posicionamento') {
    document.getElementById('objetivo-player').textContent = players.find(p => p.cor === jogadorAtual).objetivo;
  }
}


function tratarObjetivo(objetivo) {
  if (objetivo.includes('Região 1')) {
    objetivo = objetivo.replace('Região 1','Região ' + MAPEAMENTO_REGIOES['Regiao_1']);
  }
  if (objetivo.includes('Região 2')) {
    objetivo = objetivo.replace('Região 2', 'Região ' + MAPEAMENTO_REGIOES['Regiao_2']);
  }
  if (objetivo.includes('Região 3')) {
    objetivo = objetivo.replace('Região 3', 'Região ' + MAPEAMENTO_REGIOES['Regiao_3']);
  }
  if (objetivo.includes('Região 4')) {
    objetivo = objetivo.replace('Região 4', 'Região ' + MAPEAMENTO_REGIOES['Regiao_4']);
  }
  if (objetivo.includes('Região 5')) {
    objetivo = objetivo.replace('Região 5', 'Região ' + MAPEAMENTO_REGIOES['Regiao_5']);
  }
  if (objetivo.includes('Região 6')) {
    objetivo = objetivo.replace('Região 6', 'Região ' + MAPEAMENTO_REGIOES['Regiao_6']);
  }
  return objetivo;
}

fetchJogadores();
fetchTerritorios();
fetchEstadoAtual();
