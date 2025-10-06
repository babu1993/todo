import {
	Button,
	Container,
	Text,
	Title,
	Modal,
	TextInput,
	Group,
	Card,
	ActionIcon,
	Stack
} from '@mantine/core';
import { useState, useRef, useEffect } from 'react';
import { MoonStars, Sun, Trash, UserPlus} from 'tabler-icons-react';
import { AuthenticationGuard, useAuth} from '@trimblecloud/react-tid';
import {
	MantineProvider,
	ColorSchemeProvider,
} from '@mantine/core';
import { useHotkeys, useLocalStorage } from '@mantine/hooks';

export default function App() {
	const [tasks, setTasks] = useState([]);
	const [opened, setOpened] = useState(false);
	const [uopened, setUopened] = useState(false);
	const [currentTask, setCurrentTask] = useState({})
	const { getAccessTokenSilently } = useAuth();
	const [colorScheme, setColorScheme] = useLocalStorage({
		key: 'mantine-color-scheme',
		defaultValue: 'light',
		getInitialValueInEffect: true,
	});
	const toggleColorScheme = value =>
		setColorScheme(value || (colorScheme === 'dark' ? 'light' : 'dark'));

	useHotkeys([['mod+J', () => toggleColorScheme()]]);

	const taskTitle = useRef('');
	const taskSummary = useRef('');
	const newUserId = useRef('');

	async function createTask() {
	    const msg = {
				task_name: taskTitle.current.value,
				description: taskSummary.current.value,
			}
		setTasks([
			...tasks,
			msg
		]);
		const token = await getAccessTokenSilently();
	    const currentDomain = window.location.origin;
	    let data;
	    try{
            const response = await fetch(`${currentDomain}/api/tasks`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "Authorization": `Bearer ${token}`,
              },
            body: JSON.stringify(msg),
            }
            );

          if (!response.ok) {
            console.error("Error sending message:", response.statusText);
          }
          else{
            data = await response.json();
            console.log(data);
          }
        }
        catch(e){
          console.error("Error in fetch:", e);
        }
		saveTasks([
			...tasks,
			msg
		]);
	}

	async function assignTask(){
        var clonedTasks = [...tasks];

		clonedTasks.splice(currentTask.index, 1);

		setTasks(clonedTasks);

		saveTasks([...clonedTasks]);
		const token = await getAccessTokenSilently();
	    const currentDomain = window.location.origin;
	    let data;
	    try{
            const response = await fetch(`${currentDomain}/api/tasks/${currentTask.id}/reassign?new_user_id=${newUserId.current.value}`, {
            method: "PATCH",
            headers: {
              "Content-Type": "application/json",
              "Authorization": `Bearer ${token}`,
              }
            }
            );

          if (!response.ok) {
            console.error("Error sending message:", response.statusText);
          }
          else{
            data = await response.json();
            console.log(data);
          }
        }
        catch(e){
          console.error("Error in fetch:", e);
        }
	}

	async function deleteTask(index, task_id) {
		var clonedTasks = [...tasks];

		clonedTasks.splice(index, 1);

		setTasks(clonedTasks);

		saveTasks([...clonedTasks]);
        const token = await getAccessTokenSilently();
	    const currentDomain = window.location.origin;
	    let data;
	    try{
            const response = await fetch(`${currentDomain}/api/tasks/${task_id}`, {
            method: "DELETE",
            headers: {
              "Content-Type": "application/json",
              "Authorization": `Bearer ${token}`,
              }
            }
            );

          if (!response.ok) {
            console.error("Error sending message:", response.statusText);
          }
          else{
            data = await response.json();
            console.log(data);
          }
        }
        catch(e){
          console.error("Error in fetch:", e);
        }
	}

	async function loadTasks() {
	    const token = await getAccessTokenSilently();
	    const currentDomain = window.location.origin;
	    let data;
	    try{
        const response = await fetch(`${currentDomain}/api/tasks`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
            }
          });
          if (!response.ok) {
            console.error("Error sending message:", response.statusText);
          }
          else{
            data = await response.json();
            console.log(data)
          }
        }
        catch(e){
          console.error("Error in fetch:", e);
        }
        if (data) {
            setTasks(data);
        }
	}

	function saveTasks(tasks) {
		localStorage.setItem('tasks', JSON.stringify(tasks));
	}

	useEffect(() => {
	    (async () => {
            await loadTasks();
	    })();
	}, []);

	return (
	<AuthenticationGuard renderComponent={
	<ColorSchemeProvider
			colorScheme={colorScheme}
			toggleColorScheme={toggleColorScheme}>
			<MantineProvider
				theme={{ colorScheme, defaultRadius: 'md' }}
				withGlobalStyles
				withNormalizeCSS>
				<div className='App'>
				    <Modal
						opened={uopened}
						size={'md'}
						title={'Assign Task'}
						withCloseButton={false}
						onClose={() => {
							setUopened(false);
						}}
						centered>
                            <TextInput
							mt={'md'}
							ref={newUserId}
							placeholder={'User Id'}
							required
							label={'Title'}
							/>
                        <Group mt={'md'} position={'apart'}>
							<Button
								onClick={() => {
									setUopened(false);
								}}
								variant={'subtle'}>
								Cancel
							</Button>
							<Button
								onClick={async () => {
                                    await assignTask();
									setUopened(false);
								}}>
								Assign
							</Button>
						</Group>
					</Modal>
					<Modal
						opened={opened}
						size={'md'}
						title={'New Task'}
						withCloseButton={false}
						onClose={() => {
							setOpened(false);
						}}
						centered>
						<TextInput
							mt={'md'}
							ref={taskTitle}
							placeholder={'Task Title'}
							required
							label={'Title'}
						/>
						<TextInput
							ref={taskSummary}
							mt={'md'}
							placeholder={'Task Summary'}
							label={'Summary'}
						/>
						<Group mt={'md'} position={'apart'}>
							<Button
								onClick={() => {
									setOpened(false);
								}}
								variant={'subtle'}>
								Cancel
							</Button>
							<Button
								onClick={async () => {
									await createTask();
									setOpened(false);
								}}>
								Create Task
							</Button>
						</Group>
					</Modal>
					<Container size={550} my={40}>
						<Group position={'apart'}>
							<Title
								sx={theme => ({
									fontFamily: `Greycliff CF, ${theme.fontFamily}`,
									fontWeight: 900,
								})}>
								My Tasks
							</Title>
							<ActionIcon
								color={'blue'}
								onClick={() => toggleColorScheme()}
								size='lg'>
								{colorScheme === 'dark' ? (
									<Sun size={16} />
								) : (
									<MoonStars size={16} />
								)}
							</ActionIcon>
						</Group>
						{tasks.length > 0 ? (
							tasks.map((task, index) => {
								if (task.task_name) {
									return (
										<Card withBorder key={index} mt={'sm'}>
											<Group position={'apart'}>
												<Text weight={'bold'}>{task.task_name}</Text>
												<Stack align="center" justify="center">
												<ActionIcon
													onClick={async () => {
														await deleteTask(index, task.id);
													}}
													color={'red'}
													variant={'transparent'}>
													<Trash />
												</ActionIcon>
                                                <ActionIcon
													onClick={async () => {
													    setCurrentTask({
													        id: task.id,
													        index: index
													    })
													    setUopened(true);
													}}
													color={'red'}
													variant={'transparent'}>
													<UserPlus />
												</ActionIcon>
												</Stack>
											</Group>
											<Text color={'dimmed'} size={'md'} mt={'sm'}>
												{task.description
													? task.description
													: 'No summary was provided for this task'}
											</Text>
										</Card>
									);
								}
							})
						) : (
							<Text size={'lg'} mt={'md'} color={'dimmed'}>
								You have no tasks
							</Text>
						)}
						<Button
							onClick={() => {
								setOpened(true);
							}}
							fullWidth
							mt={'md'}>
							New Task
						</Button>
					</Container>
				</div>
			</MantineProvider>
		</ColorSchemeProvider>
	}/>
	);
}
