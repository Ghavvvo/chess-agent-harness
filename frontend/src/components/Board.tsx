import {Chessboard} from 'react-chessboard';
export default function Board({fen}:{fen:string}) {
 return <Chessboard options={{position:fen,allowDragging:false,darkSquareStyle:{backgroundColor:'#496b9b'},lightSquareStyle:{backgroundColor:'#dee7f2'},animationDurationInMs:0}}/>;
}
