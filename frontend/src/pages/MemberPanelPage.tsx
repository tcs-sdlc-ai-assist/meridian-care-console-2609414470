import { useEffect, useState } from 'react';
import { members } from '../api/client';
import { MemberTable } from '../components/MemberTable';
import type { MemberRow } from '../types';
export default function MemberPanelPage(): JSX.Element { const [items,setItems]=useState<MemberRow[]>([]); const [search,setSearch]=useState(''); const [error,setError]=useState(''); useEffect(()=>{members(search).then(data=>setItems(data.items)).catch(error=>setError(error.message));},[search]); return <main className="page"><h1>Member panel</h1><label htmlFor="search">Search members</label><input id="search" value={search} onChange={event=>setSearch(event.target.value)} placeholder="Name" />{error?<p role="alert">{error}</p>:<MemberTable members={items}/>}</main>; }
