'use client';

import Image from "next/image";
import { useCallback, useState, useEffect } from 'react';
import LoadingPage from "../../components/userStatePages/loading";
import ErrorPage from "../../components/userStatePages/error";

type topics = {
    id: number;
    subject_id: number;
    title: string;
    material_count: number;
    created_at: string;
    selecionado?: boolean; 
}

type MaterialList = {
    id: number;
    list: topics[];
}

interface StudyPlanModalProps {
    isOpen: boolean;
    onClose: () => void;
    subjectId: string;
}

export default function CreateStudyPlanModal({ isOpen, onClose, subjectId }: StudyPlanModalProps) {
    const [materialList, setMaterialList] = useState<MaterialList>();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (isOpen && subjectId) {
            const fetchMaterialList = async () => {
                setLoading(true);
                try {
                    const response = await fetch(`http://localhost:8080/students/subjects/topics?subjectId=${subjectId}`, {
                        method: 'GET',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${localStorage.getItem("accessToken")}`
                        }
                    });
                    
                    if (!response.ok) {
                        throw new Error('Erro ao carregar materiais');
                    }
                    
                    const data = await response.json();
                    
                    const materialsWithSelection = data.map((material: Omit<topics, 'selecionado'>) => ({
                        ...material,
                        selecionado: false 
                    }));
                    
                    setMaterialList({
                        id: 1,
                        list: materialsWithSelection
                    });
                    
                } catch (err) {
                    if (err instanceof Error) {
                        setError(err.message);
                    } else {
                        setError('Erro desconhecido');
                    }
                } finally {
                    setLoading(false);
                }
            };
            
            fetchMaterialList();
        }
    }, [isOpen, subjectId]);

    const selecionarMaterial = useCallback((materialId: number) => {
        setMaterialList(prev => {
            if (!prev) return prev;
            
            return {
                ...prev,
                list: prev.list.map(material =>
                    material.id === materialId 
                        ? { ...material, selecionado: !material.selecionado }
                        : material
                )
            };
        });
    }, []);

const handleConfirmar = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    if (!materialList) return;
    
    const selecionados = materialList.list
        .filter(material => material.selecionado)
        .map(material => material.id);
    
    if (selecionados.length === 0) {
        setError('Selecione pelo menos um material');
        setLoading(false);
        return;
    }
    
    try {
        
        console.log(JSON.stringify({
                "topicIds": selecionados
            }))

        const sendResponse = await fetch('http://localhost:8080/students/llm/transcripts/send', {
            method: 'POST',
            body: JSON.stringify({
                "topicIds": selecionados
            }),
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem("accessToken")}`
            }
        });
        
        
        const llmResponse = await sendResponse.json();
        console.log('Resposta do LLM:', llmResponse);
        
        if (!sendResponse.ok) {
            const errorText = await sendResponse.text();
            throw new Error(`Erro ao processar materiais: ${sendResponse.status} ${sendResponse.statusText}`);
        }
       
        const planData = llmResponse;
        
        const createResponse = await fetch('http://localhost:8080/students/studyplans/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem("accessToken")}`
            },
            body: JSON.stringify({
                "subjectId": Number(subjectId), 
                "planData": planData     
            })
        });
        
        if (!createResponse.ok) {
            const errorText = await createResponse.text();
            throw new Error(`Erro ao criar plano de estudos: ${createResponse.status} ${createResponse.statusText}`);
        }
        
        console.log('TESTESTES TESDE :  ' + JSON.stringify({
                "subjectId": Number(subjectId), 
                "planData": planData     
            }) );
        const createdPlan = await createResponse.json();
        console.log('Plano criado com sucesso:', createdPlan);
        
        onClose();
        
    } catch (err) {
        console.error('Erro:', err);
        if (err instanceof Error) {
            setError(err.message);
        } else {
            setError('Erro desconhecido');
        }
    } finally {
        setLoading(false);
    }
}, [materialList, onClose, subjectId]);

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
            <div className="bg-white w-full max-w-[40%] max-h-[90vh] rounded-2xl overflow-hidden flex flex-col">
                <div className="bg-[#098842] min-h-16 max-h-16 flex items-center justify-between px-6">
                    <h1 className="text-white font-medium">Criar Plano de Estudos</h1>
                    <button 
                        onClick={onClose}
                        className="w-5 h-5 cursor-pointer"
                    >
                        <Image src="/imagens/X-branco.svg" width={16} height={16} alt="Fechar"/>
                    </button>
                </div>

                {loading ? 
                    (<div className="flex items-center justify-center flex-1"><LoadingPage/></div>) 
                : error ? 
                    (<div className="flex flex-col items-center justify-center flex-1 p-6">
                        <ErrorPage/>
                        <p className="text-[#686464] mt-4 text-center">{error}</p>
                    </div>) 
                : !materialList || materialList.list.length === 0 ? (
                    <div className="flex items-center justify-center flex-1 p-6">
                        <p className="text-[#686464]">Nenhum material disponível</p>
                    </div>
                ) : (
                    <div className="flex flex-col p-6 overflow-hidden">
                        <h2 className="text-center text-sm text-[#686464] mb-4">
                            Confirme o material que você deseja incluir no plano de estudos    
                        </h2>        
                        
                        <div className="flex-1 overflow-auto mb-6">
                            <div className="bg-[#FFFFFF] rounded-lg drop-shadow p-4">
                                {materialList.list.map(material => (
                                    <div 
                                        key={material.id} 
                                        className={`flex flex-row items-center mb-3 p-3 rounded-lg transition-colors ${
                                            material.selecionado ? 'bg-[#E3E3E3]' : 'hover:bg-gray-50'
                                        }`}
                                    >
                                        <button 
                                            className="m-4 cursor-pointer flex-none"
                                            onClick={() => selecionarMaterial(material.id)}
                                        >
                                            <Image 
                                                src={material.selecionado ? '/imagens/check_box_marcada.svg' : '/imagens/check_box.svg'} 
                                                width={18} 
                                                height={18} 
                                                alt="checkbox"
                                            />
                                        </button>
                                        
                                        <div className="flex flex-col justify-center flex-1">
                                            <h3 className="text-[#686464] font-semibold text-sm">{material.title}</h3>
                                            <p className="text-[#686464] text-xs">
                                                {material.material_count} arquivo{material.material_count !== 1 ? 's' : ''} adicionado{material.material_count !== 1 ? 's' : ''}
                                            </p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="flex justify-center">
                            <button 
                                onClick={handleConfirmar}
                                disabled={loading || materialList.list.filter(m => m.selecionado).length === 0}
                                className={`w-51 h-10 cursor-pointer bg-[#098842] rounded-lg transition-colors flex items-center justify-center ${
                                    materialList.list.filter(m => m.selecionado).length === 0 
                                        ? 'opacity-50 cursor-not-allowed' 
                                        : 'hover:bg-[#087735]'
                                }`}
                            >
                                <p className="font-semibold text-white text-base">
                                    {loading ? 'Processando...' : 'Confirmar'}
                                </p>
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}