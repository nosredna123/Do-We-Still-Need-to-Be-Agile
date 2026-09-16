'use client';
import Image from "next/image";
import { useCallback, useEffect, useState } from 'react';
import LoadingPage from "../../components/userStatePages/loading";
import ErrorPage from "../../components/userStatePages/error";
import ModalConfirmacao from "../../components/userStatePages/modalConfirmarAcao";

type topics = {
    id : number;
    plan_id : number;
    title: string;
    order_index: number;
}

type task = {
    id: number;
    plan_id: number;
    order_index: number;
    title : string;
    description: string;
    completed: boolean;
}

type complementary = {
    id: number;
    plan_id: number;
    topic_title: string;
    description: string;
    order_index: number;
}

type expanded = {
    id: number;
    plan_id : number;
    topic_title: string;
    justification : string;
    order_index: number;
}

type studyplan = {
    id: number;
    userId: number;
    discipline_id: number;
    title: string;
    created_at: string;
    study_plan_topics: topics[];
    study_plans_checklist: task[];
    study_plans_complementary: complementary[];
    study_plans_expanded: expanded[]
}

interface ViewStudyPlanModalProps {
    isOpen: boolean;
    onClose: () => void;
    planId: number;
}

export default function StudyPlanModal({ isOpen, onClose, planId }: ViewStudyPlanModalProps) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [studyplan, setStudyplan] = useState<studyplan>();
    const [editingTask, setEditingTask] = useState<task | null>(null);
    const [modalTitle, setModalTitle] = useState('');
    const [modalDescription, setModalDescription] = useState('');
    const [savingTask, setSavingTask] = useState(false);
    const [hoveredTaskId, setHoveredTaskId] = useState<number | null>(null);
    const [deletingTask, setDeletingTask] = useState<task | null>(null);
    const [confirmDeleteOpen, setConfirmDeleteOpen] = useState(false);
    const [deletingLoading, setDeletingLoading] = useState(false);
    const [creatingTask, setCreatingTask] = useState(false);
    const [newTaskTitle, setNewTaskTitle] = useState('');
    const [newTaskDescription, setNewTaskDescription] = useState('');

    const toggleTaskCompletion = useCallback(async (taskId: number) => {        
        setStudyplan(prev => {
            if (!prev) return prev; 
            
            const updatedTasks = prev.study_plans_checklist.map(task =>
                task.id === taskId 
                    ? { ...task, completed: !task.completed }
                    : task
            );
            
            const taskToUpdate = updatedTasks.find(t => t.id === taskId);
            
            fetch(`http://localhost:8080/students/studyplan/checklist/mark?itemId=${taskId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
                },
                body: JSON.stringify({ completed: taskToUpdate?.completed })
            }).catch(err => {
                console.error('Erro ao atualizar tarefa:', err);
            });

            return {
                ...prev,
                study_plans_checklist: updatedTasks
            };
        });
    }, []);

    const handleEditTask = useCallback((task: task) => {
        setEditingTask(task);
        setModalTitle(task.title);
        setModalDescription(task.description);
    }, []);

    const handleSaveTask = useCallback(async () => {
        if (!editingTask || !studyplan) return;

        const updatedTask = {
            ...editingTask,
            title: modalTitle,
            description: modalDescription
        };

        setSavingTask(true);

        try {
            const response = await fetch(`http://localhost:8080/students/studyplan/checklist/edit`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
                },
                body: JSON.stringify({
                    itemId: updatedTask.id,
                    title: updatedTask.title,
                    description: updatedTask.description
                })
            });

            if (response.ok) {
                setStudyplan(prev => {
                    if (!prev) return prev;
                    
                    return {
                        ...prev,
                        study_plans_checklist: prev.study_plans_checklist.map(task =>
                            task.id === updatedTask.id ? updatedTask : task
                        )
                    };
                });
                
                setEditingTask(null);
                setModalTitle('');
                setModalDescription('');
            }
        } catch (err) {
            console.error('Erro ao salvar tarefa:', err);
        } finally {
            setSavingTask(false);
        }
    }, [editingTask, studyplan, modalTitle, modalDescription]);

    const handleCancelEdit = useCallback(() => {
        if (savingTask) return;
        setEditingTask(null);
        setModalTitle('');
        setModalDescription('');
    }, [savingTask]);

    const handleDeleteTask = useCallback((task: task) => {
        setDeletingTask(task);
        setConfirmDeleteOpen(true);
    }, []);

    const confirmDelete = useCallback(async () => {
        if (!deletingTask || !studyplan) return;

        setDeletingLoading(true);

        try {
            const response = await fetch(`http://localhost:8080/students/studyplan/checklist/delete?itemId=${deletingTask.id}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
                }
            });

            if (response.ok) {
                setStudyplan(prev => {
                    if (!prev) return prev;
                    
                    return {
                        ...prev,
                        study_plans_checklist: prev.study_plans_checklist.filter(task =>
                            task.id !== deletingTask.id
                        )
                    };
                });
                
                setConfirmDeleteOpen(false);
                setDeletingTask(null);
            }
        } catch (err) {
            console.error('Erro ao deletar tarefa:', err);
            setConfirmDeleteOpen(false);
            setDeletingTask(null);
        } finally {
            setDeletingLoading(false);
        }
    }, [deletingTask, studyplan]);

    const cancelDelete = useCallback(() => {
        if (deletingLoading) return;
        setConfirmDeleteOpen(false);
        setDeletingTask(null);
    }, [deletingLoading]);

    const handleCreateTask = useCallback(() => {
        setCreatingTask(true);
        setNewTaskTitle('');
        setNewTaskDescription('');
    }, []);

    const handleCancelCreate = useCallback(() => {
        if (savingTask) return;
        setCreatingTask(false);
        setNewTaskTitle('');
        setNewTaskDescription('');
    }, [savingTask]);

    const handleSaveNewTask = useCallback(async () => {
        if (!newTaskTitle.trim() || !studyplan) return;

        setSavingTask(true);

        try {
            const response = await fetch(`http://localhost:8080/students/studyplan/checklist/add`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
                },
                body: JSON.stringify({
                    planId: studyplan.id,
                    title: newTaskTitle,
                    description: newTaskDescription
                })
            });

            if (response.ok) {
                const newTask = await response.json();
                
                setStudyplan(prev => {
                    if (!prev) return prev;
                    
                    return {
                        ...prev,
                        study_plans_checklist: [
                            ...prev.study_plans_checklist,
                            {
                                ...newTask,
                                completed: false
                            }
                        ]
                    };
                });
                
                setCreatingTask(false);
                setNewTaskTitle('');
                setNewTaskDescription('');
            }
        } catch (err) {
            console.error('Erro ao criar tarefa:', err);
        } finally {
            setSavingTask(false);
        }
    }, [newTaskTitle, newTaskDescription, studyplan]);

    useEffect(() => {
        if (isOpen && planId) {
            const fetchStudyplanData = async() => {
                setLoading(true);
                
                try{
                    const response = await fetch(`http://localhost:8080/students/studyplan?id=${planId}`, {
                        method: 'GET',
                        headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
                        }
                    });

                    const data = await response.json();
                    setStudyplan(data)

                } catch (err) {
                    if (err instanceof Error){
                        setError(err.message);
                    } 
                } finally {
                    setLoading(false);
                } 
            }
            fetchStudyplanData();
        }
    }, [isOpen, planId]);

    if (!isOpen) return null;

    return (
        <>
            <div className="fixed inset-0 flex items-center justify-center z-50">
                <div 
                    className="absolute inset-0 bg-black opacity-75"
                    onClick={onClose}
                    aria-hidden="true"
                />
                
                <div className="relative z-50 flex flex-col w-[95vw] h-[90vh] bg-[#F5F5F5] rounded-xl overflow-hidden shadow-2xl mx-4">
                    <div className="flex flex-row justify-between items-center px-6 py-3 bg-[#098842]">
                        <h1 className="grow text-center font-semibold text-white text-lg">
                            {studyplan?.title || 'Plano de Estudos'}
                        </h1>
                        <button 
                            className="w-5 h-5 cursor-pointer flex items-center justify-center"
                            onClick={onClose}
                            aria-label="Fechar modal"
                        >
                            <Image src="/imagens/X-branco.svg" width={16} height={16} alt="Fechar"/>
                        </button>
                    </div>

                    {loading ? 
                        (<div className="flex items-center justify-center flex-1"><LoadingPage/></div>) 
                    : error ? 
                        (<div className="flex items-center justify-center flex-1"><ErrorPage/></div>) 
                    : (
                        <div className="flex flex-row justify-between min-h-[85%] p-6 gap-6 overflow-hidden">
                            <div className="flex flex-row w-[75%] min-h-full bg-white rounded-lg drop-shadow overflow-auto">
                                <div className="px-5 py-5 text-[#494949] w-full">
                                    
                                    {studyplan && (
                                        <div className="space-y-8">
                                            <div>
                                                <h2 className="text-2xl font-bold text-[#098842] mb-4">
                                                    1. Roteiro de Estudos (Tópicos Principais)
                                                </h2>
                                                        
                                                <ul className="space-y-3">
                                                    {studyplan.study_plan_topics
                                                        .sort((a, b) => a.order_index - b.order_index)
                                                        .map((topic, index) => (
                                                            <li key={topic.id} className="flex items-start">
                                                                <span className="text-[#098842] font-bold mr-3 mt-1">
                                                                    {index + 1}.
                                                                </span>
                                                                    
                                                                <div>
                                                                    <h3 className="text-lg font-semibold text-[#494949]">
                                                                        {topic.title}
                                                                    </h3>
                                                                </div>
                                                            </li>
                                                        ))
                                                    }
                                                </ul>
                                            </div>

                                            {studyplan.study_plans_expanded && studyplan.study_plans_expanded.length > 0 && (
                                                <div>
                                                    <h2 className="text-2xl font-bold text-[#098842] mb-4">
                                                        2. Roteiro Expandido e Justificativa
                                                    </h2>
                                                        
                                                    <div className="space-y-4">
                                                        {studyplan.study_plans_expanded
                                                            .sort((a, b) => a.order_index - b.order_index)
                                                            .map((expanded) => (
                                                                <div key={expanded.id} className="border-l-4 border-[#098842] pl-4 py-2">
                                                                    <h3 className="text-lg font-semibold text-[#494949] mb-2">
                                                                        {expanded.topic_title}
                                                                    </h3>
                                                                                
                                                                    <div className="bg-gray-50 p-4 rounded-md">
                                                                        <p className="text-sm text-gray-700">
                                                                            <span className="font-semibold text-[#098842]">Justificativa:</span> {expanded.justification}
                                                                        </p>
                                                                    </div>
                                                                </div>
                                                            ))
                                                        }
                                                    </div>
                                                </div>
                                                )}

                                            {studyplan.study_plans_complementary && studyplan.study_plans_complementary.length > 0 && (
                                                <div>
                                                    <h2 className="text-2xl font-bold text-[#098842] mb-4">
                                                        3. Conteúdos Complementares
                                                    </h2>
                                                        
                                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                                        {studyplan.study_plans_complementary
                                                            .sort((a, b) => a.order_index - b.order_index)
                                                        .map((complementary) => (
                                                                
                                                            <div key={complementary.id} className="bg-gray-50 p-4 rounded-lg">
                                                                <h3 className="text-lg font-semibold text-[#494949] mb-2">
                                                                    {complementary.topic_title}
                                                                </h3>
                                                                <p className="text-sm text-gray-700">
                                                                    {complementary.description}
                                                                </p>
                                                            </div>
                                                        ))
                                                        }
                                                    </div>
                                                </div>
                                                )}
                                        </div>
                                    )}
                                </div>
                            </div>

                            <div className="w-[25%] min-h-full bg-white rounded-lg drop-shadow gap-2 overflow-auto">
                                <button 
                                    className="flex justify-center p-1 m-0.5 font-semibold text-[#686464] items-center gap-2 w-full hover:bg-gray-50 rounded cursor-pointer"
                                    onClick={handleCreateTask}
                                >
                                    <Image src="/imagens/add-cinza.svg" width={16} height={16} alt="adicionar" />
                                    <h2>Adicionar Item</h2>
                                </button>

                                {(studyplan?.study_plans_checklist || []).map(task => (
                                    <div 
                                        key={task.id} 
                                        className={`flex flex-row ${task.completed ? 'bg-[#E3E3E3] line-through decoration-[#686464]' : ''} ${hoveredTaskId === task.id && !task.completed ? 'bg-gray-50' : ''}`}
                                        onMouseEnter={() => setHoveredTaskId(task.id)}
                                        onMouseLeave={() => setHoveredTaskId(null)}
                                    >
                                        <button 
                                            className="m-4 cursor-pointer flex-none"
                                            onClick={() => toggleTaskCompletion(task.id)}
                                        >
                                            <Image 
                                                src={task.completed ? '/imagens/check_box_marcada.svg' : '/imagens/check_box.svg'} 
                                                width={18} 
                                                height={18} 
                                                alt="checkbox"
                                            />
                                        </button>
                                        
                                        <div className="flex flex-col max-h-[65%] justify-center m-1.5 flex-1">
                                            <h3 className="text-[#686464] font-semibold text-sm">{task.title}</h3>
                                            <p className="text-[#686464] text-xs">{task.description}</p>
                                        </div>

                                        <div className="flex flex-col m-3 justify-center gap-1.5">
                                            <button 
                                                className="w-5 h-5 cursor-pointer"
                                                onClick={() => handleEditTask(task)}
                                                disabled={task.completed}
                                            >
                                                <Image src="/imagens/editar-cinza.svg" width={16} height={16} alt="Editar" />
                                            </button>

                                            <button 
                                                className="w-5 h-5 cursor-pointer"
                                                onClick={() => handleDeleteTask(task)}
                                                disabled={task.completed}
                                            >
                                                <Image src="/imagens/apagar-cinza.svg" width={16} height={16} alt="Deletar" />
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {editingTask && (
                        <div className="fixed inset-0 flex items-center justify-center z-60">
                            <div 
                                className="absolute inset-0 bg-black opacity-75"
                                onClick={handleCancelEdit}
                                aria-hidden="true"
                            />
                            
                            <div className="relative z-61 flex flex-col w-[90vw] max-w-[500px] bg-[#F5F5F5] rounded-xl overflow-hidden shadow-2xl mx-4">
                                <div className="flex flex-row justify-between items-center px-6 py-4 bg-[#098842]">
                                    <h1 className="grow text-center font-semibold text-white text-lg">
                                        Editar Tarefa
                                    </h1>
                                    <button 
                                        className="w-6 h-6 cursor-pointer flex items-center justify-center"
                                        onClick={handleCancelEdit}
                                        aria-label="Fechar modal"
                                        disabled={savingTask}
                                    >
                                        <Image src="/imagens/X-branco.svg" width={16} height={16} alt="Fechar"/>
                                    </button>
                                </div>
                                
                                <div className="grow p-6 space-y-4">
                                    <div>
                                        <label className="block font-medium text-[#494949] text-base mb-2">
                                            Título
                                        </label>
                                        <input
                                            type="text"
                                            value={modalTitle}
                                            onChange={(e) => setModalTitle(e.target.value)}
                                            className="text-[#494949] w-full px-3 py-2 rounded-md focus:outline-none border-2 border-[#818181] focus:border-[#494949] hover:border-gray-400 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                                            autoFocus
                                            disabled={savingTask}
                                        />
                                    </div>
                                    
                                    <div>
                                        <label className="block font-medium text-[#494949] text-base mb-2">
                                            Descrição
                                        </label>
                                        <textarea
                                            value={modalDescription}
                                            onChange={(e) => setModalDescription(e.target.value)}
                                            className="text-[#494949] w-full px-3 py-2 rounded-md focus:outline-none border-2 border-[#818181] focus:border-[#494949] hover:border-gray-400 transition-colors duration-200 resize-none disabled:opacity-50 disabled:cursor-not-allowed"
                                            rows={4}
                                            disabled={savingTask}
                                        />
                                    </div>
                                </div>
                                
                                <div className="flex flex-row justify-center gap-4 px-6 py-4">
                                    <button 
                                        className="w-32 h-11 cursor-pointer bg-[#098842] rounded-lg hover:bg-[#087735] transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                                        onClick={handleSaveTask}
                                        disabled={savingTask}
                                    >
                                        {savingTask ? (
                                            <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
                                        ) : (
                                            <p className="font-semibold text-white text-sm">
                                                Salvar
                                            </p>
                                        )}
                                    </button>
                                    
                                    <button 
                                        className="w-32 h-11 cursor-pointer bg-[#D9D9D9] rounded-lg hover:bg-[#c4c4c4] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                        onClick={handleCancelEdit}
                                        disabled={savingTask}
                                    >
                                        <p className="font-semibold text-[#444444] text-sm">
                                            Cancelar
                                        </p>
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}

                    {creatingTask && (
                        <div className="fixed inset-0 flex items-center justify-center z-60">
                            <div 
                                className="absolute inset-0 bg-black opacity-75"
                                onClick={handleCancelCreate}
                                aria-hidden="true"
                            />
                            
                            <div className="relative z-61 flex flex-col w-[90vw] max-w-[500px] bg-[#F5F5F5] rounded-xl overflow-hidden shadow-2xl mx-4">
                                <div className="flex flex-row justify-between items-center px-6 py-4 bg-[#098842]">
                                    <h1 className="grow text-center font-semibold text-white text-lg">
                                        Criar Nova Tarefa
                                    </h1>
                                    <button 
                                        className="w-6 h-6 cursor-pointer flex items-center justify-center"
                                        onClick={handleCancelCreate}
                                        aria-label="Fechar modal"
                                        disabled={savingTask}
                                    >
                                        <Image src="/imagens/X-branco.svg" width={16} height={16} alt="Fechar"/>
                                    </button>
                                </div>
                                
                                <div className="grow p-6 space-y-4">
                                    <div>
                                        <label className="block font-medium text-[#494949] text-base mb-2">
                                            Título *
                                        </label>
                                        <input
                                            type="text"
                                            value={newTaskTitle}
                                            onChange={(e) => setNewTaskTitle(e.target.value)}
                                            className="text-[#494949] w-full px-3 py-2 rounded-md focus:outline-none border-2 border-[#818181] focus:border-[#494949] hover:border-gray-400 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                                            placeholder="Digite o título da tarefa"
                                            autoFocus
                                            disabled={savingTask}
                                        />
                                    </div>
                                    
                                    <div>
                                        <label className="block font-medium text-[#494949] text-base mb-2">
                                            Descrição
                                        </label>
                                        <textarea
                                            value={newTaskDescription}
                                            onChange={(e) => setNewTaskDescription(e.target.value)}
                                            className="text-[#494949] w-full px-3 py-2 rounded-md focus:outline-none border-2 border-[#818181] focus:border-[#494949] hover:border-gray-400 transition-colors duration-200 resize-none disabled:opacity-50 disabled:cursor-not-allowed"
                                            placeholder="Digite a descrição da tarefa (opcional)"
                                            rows={4}
                                            disabled={savingTask}
                                        />
                                    </div>
                                </div>
                                
                                <div className="flex flex-row justify-center gap-4 px-6 py-4">
                                    <button 
                                        className="w-32 h-11 cursor-pointer bg-[#098842] rounded-lg hover:bg-[#087735] transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                                        onClick={handleSaveNewTask}
                                        disabled={savingTask || !newTaskTitle.trim()}
                                    >
                                        {savingTask ? (
                                            <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
                                        ) : (
                                            <p className="font-semibold text-white text-sm">
                                                Criar
                                            </p>
                                        )}
                                    </button>
                                    
                                    <button 
                                        className="w-32 h-11 cursor-pointer bg-[#D9D9D9] rounded-lg hover:bg-[#c4c4c4] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                        onClick={handleCancelCreate}
                                        disabled={savingTask}
                                    >
                                        <p className="font-semibold text-[#444444] text-sm">
                                            Cancelar
                                        </p>
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            <ModalConfirmacao
                isOpen={confirmDeleteOpen}
                titulo="Confirmar Exclusão"
                mensagem={`Tem certeza que deseja excluir a tarefa "${deletingTask?.title}"? Esta ação não pode ser desfeita.`}
                onConfirmar={confirmDelete}
                onCancelar={cancelDelete}
                loading={deletingLoading}
            />
        </>
    );
}