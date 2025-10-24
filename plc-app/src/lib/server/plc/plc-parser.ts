/**
 * PLC Data Parser
 * 
 * Parses and validates the 8-byte array received from the PLC
 * according to the contract specification.
 */

export interface PLCPacket {
	raw: number[];
	generalStatus: GeneralStatus;
	pieceStatus: PieceStatus;
	failureCode: FailureCode;
	modelId: number;
	cameraStatus: number;
	electricalStatus: number;
	readyFlag: number;
	reserved: number;
}

export enum GeneralStatus {
	RUNNING = 0,
	STOPPED = 1,
	ERROR = 2,
	MAINTENANCE = 3
}

export enum PieceStatus {
	OK = 0,
	NOK = 1
}

export enum FailureCode {
	NO_FAILURE = 0,
	HIPOT_FAILURE = 1,
	INCORRECT_LABEL = 2,
	INCORRECT_MODEL = 3,
	INCORRECT_TERMINAL = 4,
	UNKNOWN = 99
}

export interface ParsedPieceResult {
	timestamp: Date;
	modelId: number;
	pieceStatus: 'OK' | 'NOK';
	failureType: string;
	cameraStatus: number;
	electricalStatus: number;
	lineStatus: 'RUNNING' | 'ERROR' | 'MAINTENANCE' | 'STOPPED';
	isValid: boolean;
	rawData: number[];
}

/**
 * Validates that the packet has exactly 8 elements and all are valid numbers (0-9)
 */
export function validatePacket(data: any): data is number[] {
	if (!Array.isArray(data)) {
		console.error('[PLC Parser] Data is not an array:', data);
		return false;
	}

	if (data.length !== 8) {
		console.error(`[PLC Parser] Invalid packet length: ${data.length}, expected 8`);
		return false;
	}

	const allValid = data.every(
		(value) => typeof value === 'number' && value >= 0 && value <= 9
	);

	if (!allValid) {
		console.error('[PLC Parser] Packet contains invalid values:', data);
		return false;
	}

	return true;
}

/**
 * Parses raw PLC packet into structured data
 */
export function parsePacket(raw: number[]): PLCPacket {
	return {
		raw,
		generalStatus: raw[0] as GeneralStatus,
		pieceStatus: raw[1] as PieceStatus,
		failureCode: raw[2] as FailureCode,
		modelId: raw[3],
		cameraStatus: raw[4],
		electricalStatus: raw[5],
		readyFlag: raw[6],
		reserved: raw[7]
	};
}

/**
 * Maps failure code to human-readable description
 */
export function getFailureDescription(code: FailureCode): string {
	switch (code) {
		case FailureCode.NO_FAILURE:
			return 'Sin falla';
		case FailureCode.HIPOT_FAILURE:
			return 'Test hipot falla';
		case FailureCode.INCORRECT_LABEL:
			return 'Etiqueta incorrecta';
		case FailureCode.INCORRECT_MODEL:
			return 'Modelo incorrecto';
		case FailureCode.INCORRECT_TERMINAL:
			return 'Terminal incorrecta';
		default:
			return 'Falla desconocida';
	}
}

/**
 * Maps general status to line status string
 */
export function getLineStatus(status: GeneralStatus): ParsedPieceResult['lineStatus'] {
	switch (status) {
		case GeneralStatus.RUNNING:
			return 'RUNNING';
		case GeneralStatus.ERROR:
			return 'ERROR';
		case GeneralStatus.MAINTENANCE:
			return 'MAINTENANCE';
		case GeneralStatus.STOPPED:
			return 'STOPPED';
		default:
			return 'STOPPED';
	}
}

/**
 * Converts PLCPacket to normalized PieceResult for database storage
 */
export function parsePieceResult(packet: PLCPacket): ParsedPieceResult {
	const isValid = packet.readyFlag === 1;

	return {
		timestamp: new Date(),
		modelId: packet.modelId,
		pieceStatus: packet.pieceStatus === PieceStatus.OK ? 'OK' : 'NOK',
		failureType: getFailureDescription(packet.failureCode),
		cameraStatus: packet.cameraStatus,
		electricalStatus: packet.electricalStatus,
		lineStatus: getLineStatus(packet.generalStatus),
		isValid,
		rawData: packet.raw
	};
}

/**
 * Main function to validate and parse PLC data
 */
export function processPLCData(data: any): ParsedPieceResult | null {
	// Validate packet structure
	if (!validatePacket(data)) {
		return null;
	}

	// Parse the packet
	const packet = parsePacket(data);

	// Convert to normalized format
	const result = parsePieceResult(packet);

	// Log for debugging
	console.log('[PLC Parser] Processed:', {
		raw: result.rawData,
		status: result.pieceStatus,
		failure: result.failureType,
		line: result.lineStatus,
		valid: result.isValid
	});

	return result;
}

