import {useEffect,useRef,useState} from 'react';
import {Chess} from 'chess.js';
import Board from './components/Board';

type Phase = 'idle'|'running'|'paused'|'finished';

function gameOverMessage(reason:string, result:string){
 const messages:Record<string,string>={max_plies:'La partida terminó al alcanzar el límite de jugadas.',checkmate:`Jaque mate. Resultado: ${result}.`,stalemate:'La partida terminó en tablas por ahogado.',draw:'La partida terminó en tablas.',illegal_move:'La partida se detuvo por una jugada no válida.',agent_error:'La partida se detuvo porque un agente no respondió.',configuration_error:'No se pudo iniciar la partida. Revisa la configuración.'};
 return messages[reason]??'La partida ha terminado.';
}

export default function App(){
 const initialFen=new Chess().fen();
 const socketRef=useRef<WebSocket|null>(null);
 const [history,setHistory]=useState([initialFen]);
 const [moves,setMoves]=useState<string[]>([]);
 const [cursor,setCursor]=useState<number|null>(null);
 const [phase,setPhase]=useState<Phase>('idle');
 const [connected,setConnected]=useState(false);
 const [players,setPlayers]=useState(['—','—']);
 const [status,setStatus]=useState('Preparando la mesa…');
 const [notice,setNotice]=useState('');
 const send=(type:string)=>socketRef.current?.readyState===WebSocket.OPEN&&socketRef.current.send(JSON.stringify({type}));

 useEffect(()=>{
  let closed=false,timer:ReturnType<typeof setTimeout>,socket:WebSocket;
  const connect=()=>{
   socket=new WebSocket(`${location.protocol==='https:'?'wss':'ws'}://${location.host}/ws`);
   socketRef.current=socket;
   socket.onopen=()=>{setConnected(true);setStatus('Lista para comenzar.');};
   socket.onmessage=({data})=>{
    const e=JSON.parse(data);
    if(e.type==='game_started'){setPlayers([e.white,e.black]);setHistory([e.fen]);setMoves([]);setCursor(null);setNotice('');setPhase('running');setStatus('Partida en curso.');}
    if(e.type==='move'){setHistory(value=>[...value,e.fen]);setMoves(value=>[...value,e.move_uci]);}
    if(e.type==='control'){setPhase(e.state);setStatus(e.state==='paused'?'Partida en pausa.':'Partida en curso.');}
    if(e.type==='game_reset'){setHistory([e.fen]);setMoves([]);setCursor(null);setPlayers(['—','—']);setNotice('');setPhase('idle');setStatus('Tablero reiniciado.');}
    if(e.type==='illegal')setNotice(`Jugada no válida. El sistema continuó con ${e.fallback??'otra jugada'}.`);
    if(e.type==='agent_error')setNotice('Un agente no respondió. Revisa su configuración.');
    if(e.type==='game_over'){setPhase('finished');setStatus(gameOverMessage(e.reason,e.result));}
   };
   socket.onclose=()=>{if(!closed){setConnected(false);setStatus('Intentando recuperar la conexión…');timer=setTimeout(connect,2000);}};
  };
  connect();
  return()=>{closed=true;clearTimeout(timer);socket.close();};
 },[]);

 const index=cursor??history.length-1;
 const viewedFen=history[index]??initialFen;
 const playPause=()=>{if(phase==='running')send('pause');else if(phase==='paused')send('resume');else send('start');};
 const previous=()=>setCursor(Math.max(0,index-1));
 const next=()=>setCursor(index+1>=history.length-1?null:index+1);

 return <><a className="skip" href="#board">Saltar al tablero</a><main>
  <header><a className="brand" href="/"><span aria-hidden="true">♞</span> Chess agent harness</a></header>
  <section className="workspace" aria-labelledby="page-title">
   <div className="board-column">
    <h1 id="page-title">Mesa de juego</h1>
    <div className="player"><span><i className="piece-dot black" aria-hidden="true"/>Negras</span><strong>{players[1]}</strong></div>
    <div id="board" className="board-frame" aria-label={`Tablero de ajedrez. Juegan ${viewedFen.split(' ')[1]==='w'?'blancas':'negras'}`}><Board fen={viewedFen}/></div>
    <div className="player"><span><i className="piece-dot white" aria-hidden="true"/>Blancas</span><strong>{players[0]}</strong></div>
   </div>
   <aside className="side-panel" aria-label="Controles e historial">
    <div className="toolbar" aria-label="Controles de la partida">
     <button className="play" disabled={!connected} onClick={playPause} aria-label={phase==='running'?'Pausar partida':phase==='paused'?'Reanudar partida':'Comenzar partida'}><span aria-hidden="true">{phase==='running'?'Ⅱ':'▶'}</span><b>{phase==='running'?'Pausar':'Play'}</b></button>
     <button disabled={!connected||phase==='idle'} onClick={()=>send('stop')} aria-label="Detener y reiniciar la partida"><span aria-hidden="true">■</span><b>Stop</b></button>
     <button disabled={index===0} onClick={previous}><span aria-hidden="true">‹</span><b>Anterior</b></button>
     <button disabled={index===history.length-1} onClick={next}><b>Siguiente</b><span aria-hidden="true">›</span></button>
    </div>
    <div className="status-block"><p className="game-status" role="status" aria-live="polite">{status}</p>{notice&&<p className="notice" role="alert">{notice}</p>}</div>
    <section className="history" aria-labelledby="history-title">
     <div className="history-heading"><h2 id="history-title">Movimientos</h2><span>{moves.length}</span></div>
     <div className="scores" tabIndex={0} aria-label="Historial de movimientos"><table><caption className="sr-only">Movimientos de blancas y negras en notación UCI</caption><thead><tr><th scope="col">N.º</th><th scope="col">Blancas</th><th scope="col">Negras</th></tr></thead><tbody>
      {Array.from({length:Math.ceil(moves.length/2)},(_,i)=><tr key={i} className={index===i*2+1||index===i*2+2?'current-row':undefined}><th scope="row">{i+1}</th><td>{moves[i*2]??'—'}</td><td>{moves[i*2+1]??'—'}</td></tr>)}
     </tbody></table>{!moves.length&&<div className="empty-state"><span aria-hidden="true">♙</span><p>La partida comenzará desde esta posición.</p></div>}</div>
    </section>
   </aside>
  </section>
 </main></>;
}
