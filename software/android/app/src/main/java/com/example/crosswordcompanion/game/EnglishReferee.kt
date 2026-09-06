package com.example.crosswordcompanion.game

import com.example.crosswordcompanion.model.Board4x4
import com.example.crosswordcompanion.model.BoardCell
import com.example.crosswordcompanion.model.SquareType
import com.example.crosswordcompanion.model.Tile
import java.io.BufferedReader
import java.io.File
import java.io.InputStream
import java.io.InputStreamReader

data class RefereeResult(
    val isValid: Boolean,
    val score: Int,
    val words: List<String>,
    val message: String
)

class EnglishReferee {
    companion object {
        /**
         * Official English Scrabble letter scores
         */
        val LETTER_SCORES: Map<Char, Int> = mapOf(
            'A' to 1, 'B' to 3, 'C' to 3, 'D' to 2, 'E' to 1,
            'F' to 4, 'G' to 2, 'H' to 4, 'I' to 1, 'J' to 8,
            'K' to 5, 'L' to 1, 'M' to 3, 'N' to 1, 'O' to 1,
            'P' to 3, 'Q' to 10, 'R' to 1, 'S' to 1, 'T' to 1,
            'U' to 1, 'V' to 4, 'W' to 4, 'X' to 8, 'Y' to 4,
            'Z' to 10
        )

        /**
         * Quick fallback words (ENABLE1 common subset) used before dictionary file loads
         */
        val FALLBACK_DICTIONARY: Set<String> = setOf(
            "AA", "AB", "AD", "AE", "AG", "AH", "AI", "AL", "AM", "AN", "AR", "AS", "AT", "AW", "AX", "AY",
            "BA", "BE", "BI", "BO", "BY", "DA", "DE", "DO", "ED", "EF", "EH", "EL", "EM", "EN", "ER", "ES",
            "ET", "EW", "EX", "FA", "FE", "GO", "HA", "HE", "HI", "HM", "HO", "ID", "IF", "IN", "IS", "IT",
            "JO", "KA", "KI", "LA", "LI", "LO", "MA", "ME", "MI", "MM", "MO", "MU", "MY", "NA", "NE", "NO",
            "NU", "OD", "OE", "OF", "OH", "OI", "OK", "OM", "ON", "OP", "OR", "OS", "OW", "OX", "OY", "PA",
            "PE", "PI", "PO", "QI", "RE", "SH", "SI", "SO", "TA", "TE", "TI", "TO", "UH", "UM", "UN", "UP",
            "US", "UT", "WE", "WO", "XI", "XU", "YA", "YE", "YO", "ZA",
            "ACT", "ADD", "AGE", "AGO", "AID", "AIM", "AIR", "ALL", "AND", "ANT", "ANY", "APE", "ARM", "ART",
            "ASK", "BAD", "BAG", "BAR", "BAT", "BAY", "BED", "BEE", "BEG", "BET", "BIG", "BIN", "BIT", "BOB",
            "BOX", "BOY", "BUS", "BUT", "BUY", "BYE", "CAN", "CAP", "CAR", "CAT", "COW", "CRY", "CUP", "CUT",
            "DAD", "DAM", "DAY", "DOG", "DOT", "DRY", "DUE", "EAR", "EAT", "EGG", "END", "EYE", "FAN", "FAR",
            "FAT", "FEW", "FIT", "FLY", "FOG", "FOR", "FOX", "FUN", "FUR", "GAP", "GAS", "GET", "GOD", "GUN",
            "GUY", "HAT", "HEN", "HEY", "HIM", "HIP", "HIS", "HIT", "HOT", "HOW", "HUG", "ICE", "ILL", "INK",
            "INN", "JAR", "JAW", "JAY", "JET", "JOB", "JOY", "KEY", "KID", "KIT", "LAB", "LAP", "LAW", "LAY",
            "LEG", "LET", "LID", "LIE", "LIP", "LOG", "LOT", "LOW", "MAD", "MAN", "MAP", "MAT", "MAY", "MEN",
            "MET", "MIX", "MOM", "MUD", "MUG", "NET", "NEW", "NOD", "NOT", "NOW", "NUT", "OAK", "OAR", "ODD",
            "OFF", "OIL", "OLD", "ONE", "OUR", "OUT", "OWL", "PAN", "PAY", "PEA", "PEN", "PET", "PIG", "PIN",
            "PIT", "POT", "PRO", "RAG", "RAM", "RAN", "RAT", "RAW", "RED", "RIB", "RID", "ROD", "ROW", "RUB",
            "RUG", "RUN", "SAD", "SAW", "SAY", "SEA", "SEE", "SET", "SEW", "SHY", "SIN", "SIP", "SIR", "SIT",
            "SIX", "SKI", "SKY", "SON", "SUN", "TAB", "TAG", "TAN", "TAP", "TAX", "TEA", "TEN", "THE", "TIE",
            "TIN", "TIP", "TOE", "TOP", "TOY", "TUB", "TWO", "USE", "VAN", "VET", "WAR", "WAY", "WET", "WHO",
            "WIN", "YES", "YET", "YOU", "ZIP", "ZOO",
            "ABLE", "ACRE", "AGED", "ALTO", "AREA", "ARMY", "AUNT", "AWAY", "BABY", "BACK", "BAKE", "BALL",
            "BAND", "BANK", "BARE", "BARK", "BARN", "BASE", "BATH", "BEAM", "BEAN", "BEAR", "BEAT", "BEEF",
            "BEER", "BELL", "BELT", "BEND", "BENT", "BEST", "BILL", "BIRD", "BITE", "BLOW", "BLUE", "BOAT",
            "BODY", "BOMB", "BOND", "BONE", "BOOK", "BOOM", "BORN", "BOSS", "BOWL", "BULK", "BURN", "BUSH",
            "BUSY", "CAKE", "CALL", "CALM", "CAMP", "CARD", "CARE", "CASE", "CASH", "CAST", "CAVE", "CELL",
            "CHAT", "CHEF", "CITY", "CLAN", "CLAY", "CLIP", "CLUB", "COAL", "COAT", "CODE", "COLD", "COME",
            "COOK", "COOL", "COPE", "COPY", "CORE", "CORN", "COST", "CREW", "CROP", "DARK", "DATA", "DATE",
            "DAWN", "DEAD", "DEAL", "DEAR", "DECK", "DEED", "DEEP", "DEER", "DESK", "DIAL", "DIRT", "DISH",
            "DISK", "DOOR", "DOSE", "DOWN", "DRAW", "DROP", "DRUG", "DUCK", "DUST", "DUTY", "EACH", "EARN",
            "EAST", "EASY", "EDGE", "ELSE", "EVEN", "EVER", "FACE", "FACT", "FAIL", "FAIR", "FALL", "FARM",
            "FAST", "FATE", "FEAR", "FEED", "FEEL", "FILE", "FILL", "FILM", "FIND", "FINE", "FIRE", "FIRM",
            "FISH", "FIST", "FLAT", "FLOW", "FOOD", "FOOT", "FORD", "FORK", "FORM", "FORT", "FOUR", "FREE",
            "FROG", "FROM", "FUEL", "FULL", "FUND", "GAIN", "GAME", "GATE", "GEAR", "GIFT", "GIRL", "GIVE",
            "GLAD", "GOAL", "GOAT", "GOLD", "GOLF", "GOOD", "GRAB", "GREW", "GROW", "GULF", "HAIR", "HALF",
            "HALL", "HAND", "HANG", "HARD", "HARM", "HATE", "HAVE", "HEAD", "HEAR", "HEAT", "HELD", "HELL",
            "HELP", "HERO", "HIGH", "HILL", "HIRE", "HOLD", "HOLE", "HOLY", "HOME", "HOOK", "HOPE", "HORN",
            "HOSE", "HOST", "HOUR", "HUGE", "HUNG", "HUNT", "HURT", "IDEA", "INCH", "INTO", "IRON", "ITEM",
            "JOIN", "JUMP", "JUST", "KEEP", "KEPT", "KICK", "KILL", "KIND", "KING", "KISS", "KNEE", "KNEW",
            "KNOW", "LACK", "LADY", "LAID", "LAKE", "LAND", "LANE", "LAST", "LATE", "LEAD", "LEAF", "LEAN",
            "LEFT", "LEND", "LESS", "LIFE", "LIFT", "LIKE", "LINE", "LINK", "LION", "LIST", "LIVE", "LOAD",
            "LOAN", "LOCK", "LOGO", "LONG", "LOOK", "LORD", "LOSE", "LOSS", "LOST", "LOVE", "LUCK", "MADE",
            "MAIL", "MAIN", "MAKE", "MALE", "MANY", "MARK", "MASS", "MEAL", "MEAN", "MEAT", "MEET", "MENU",
            "MESS", "MILE", "MILK", "MIND", "MINE", "MISS", "MODE", "MOOD", "MOON", "MORE", "MOST", "MOVE",
            "MUCH", "NAME", "NAVY", "NEAR", "NECK", "NEED", "NEWS", "NEXT", "NICE", "NINE", "NONE", "NOSE",
            "NOTE", "ONCE", "ONLY", "OPEN", "ORAL", "OVER", "PACE", "PACK", "PAGE", "PAID", "PAIN", "PAIR",
            "PALM", "PARK", "PART", "PASS", "PAST", "PATH", "PEAK", "PICK", "PILE", "PIPE", "PLAN", "PLAY",
            "PLOT", "PLUG", "POEM", "POET", "POLL", "POOL", "POOR", "PORT", "POST", "PULL", "PURE", "PUSH",
            "RACE", "RAIL", "RAIN", "RANK", "RARE", "RATE", "READ", "REAL", "REAR", "RELY", "RENT", "REST",
            "RICE", "RICH", "RIDE", "RING", "RISE", "RISK", "ROAD", "ROCK", "ROLE", "ROOF", "ROOM", "ROOT",
            "ROSE", "RULE", "RUSH", "SAFE", "SAID", "SAIL", "SALE", "SALT", "SAME", "SAND", "SAVE", "SEAT",
            "SEED", "SEEK", "SEEM", "SEEN", "SELF", "SELL", "SEND", "SENT", "SHIP", "SHOE", "SHOP", "SHOT",
            "SHOW", "SHUT", "SICK", "SIDE", "SIGN", "SILK", "SITE", "SIZE", "SKIN", "SLIP", "SLOW", "SNOW",
            "SOAP", "SOFT", "SOIL", "SOLD", "SOLE", "SOME", "SONG", "SOON", "SORT", "SOUL", "SOUP", "SPOT",
            "STAR", "STAY", "STEP", "STOP", "SUCH", "SUIT", "SURE", "SWIM", "TAIL", "TAKE", "TALE", "TALK",
            "TALL", "TANK", "TAPE", "TASK", "TEAM", "TELL", "TEND", "TERM", "TEST", "TEXT", "THAN", "THAT",
            "THEM", "THEN", "THEY", "THIN", "THIS", "TIDE", "TILL", "TIME", "TINY", "TIRE", "TOLL", "TONE",
            "TOOK", "TOOL", "TOUR", "TOWN", "TREE", "TRIP", "TRUE", "TUBE", "TUNE", "TURN", "TWIN", "TYPE",
            "UNIT", "UPON", "USED", "USER", "VARY", "VAST", "VERY", "VICE", "VIEW", "VOTE", "WAGE", "WAIT",
            "WAKE", "WALK", "WALL", "WANT", "WARM", "WARN", "WASH", "WAVE", "WEAK", "WEAR", "WEEK", "WELL",
            "WENT", "WEST", "WHAT", "WHEN", "WHOM", "WIDE", "WIFE", "WILD", "WILL", "WIND", "WINE", "WING",
            "WIPE", "WIRE", "WISE", "WISH", "WITH", "WOOD", "WOOL", "WORD", "WORE", "WORK", "YARD", "YEAR",
            "ZERO", "ZONE", "HELLO", "HONEY", "QUIZ", "ZYGOTE", "SCRABBLE", "CROSSWORD"
        )

        fun getLetterScore(letter: Char): Int {
            return LETTER_SCORES[letter.uppercaseChar()] ?: 1
        }
    }

    private val dictionaryWords: HashSet<String> = HashSet(FALLBACK_DICTIONARY)

    val wordCount: Int
        get() = dictionaryWords.size

    /**
     * Loads tournament words from an InputStream (e.g. assets/dict_en.txt)
     * Mirrors the webapp workflow: reads lines, trims, filters words of length 2..15.
     */
    fun loadDictionary(inputStream: InputStream): Int {
        BufferedReader(InputStreamReader(inputStream, Charsets.UTF_8)).use { reader ->
            var line = reader.readLine()
            while (line != null) {
                val word = line.trim().uppercase()
                if (word.length in 2..15) {
                    dictionaryWords.add(word)
                }
                line = reader.readLine()
            }
        }
        return dictionaryWords.size
    }

    /**
     * Loads dictionary from a File directly (useful for tests and offline processing).
     */
    fun loadDictionary(file: File): Int {
        return file.inputStream().use { loadDictionary(it) }
    }

    fun isWordValid(word: String): Boolean {
        return dictionaryWords.contains(word.uppercase())
    }

    /**
     * Evaluates uncommitted tiles on a 4x4 grid:
     * - Checks alignment (single row or single col)
     * - Checks no internal gaps
     * - Checks word validity in dictionary
     * - Calculates letter bonuses and word multipliers
     */
    fun evaluateMove(
        allCells: List<BoardCell>,
        uncommittedCells: List<BoardCell>,
        isFirstMove: Boolean
    ): RefereeResult {
        if (uncommittedCells.isEmpty()) {
            return RefereeResult(false, 0, emptyList(), "Place at least one tile to play.")
        }

        // On turn 1, must cover the center star (1, 1)
        if (isFirstMove) {
            val coversCenter = uncommittedCells.any { it.row == 1 && it.col == 1 }
            if (!coversCenter) {
                return RefereeResult(false, 0, emptyList(), "First move must cover the center star (row 2, col 2).")
            }
        }

        val rows = uncommittedCells.map { it.row }.toSet()
        val cols = uncommittedCells.map { it.col }.toSet()

        val isHorizontal = rows.size == 1
        val isVertical = cols.size == 1

        if (!isHorizontal && !isVertical) {
            return RefereeResult(false, 0, emptyList(), "Tiles must be placed in a single straight line.")
        }

        // Build a fast 2D lookup
        val grid = Array(Board4x4.SIZE) { r ->
            Array<BoardCell?>(Board4x4.SIZE) { c ->
                allCells.find { it.row == r && it.col == c }
            }
        }

        // Find word span
        val formedWords = mutableListOf<String>()
        var totalScore = 0

        if (isHorizontal) {
            val r = rows.first()
            val minCol = uncommittedCells.minOf { it.col }
            val maxCol = uncommittedCells.maxOf { it.col }

            // Check no gaps in span
            for (c in minCol..maxCol) {
                val cell = grid[r][c]
                if (cell?.tile == null) {
                    return RefereeResult(false, 0, emptyList(), "Tiles cannot have empty gaps between them.")
                }
            }

            // Expand to full word (including pre-existing touching tiles)
            var startCol = minCol
            while (startCol > 0 && grid[r][startCol - 1]?.tile != null) startCol--
            var endCol = maxCol
            while (endCol < Board4x4.SIZE - 1 && grid[r][endCol + 1]?.tile != null) endCol++

            val wordChars = mutableListOf<Char>()
            var wordLetterPoints = 0
            var wordMultiplier = 1

            for (c in startCol..endCol) {
                val cell = grid[r][c]!!
                val t = cell.tile!!
                wordChars.add(t.letter)

                var letterScore = getLetterScore(t.letter)
                // Bonus squares only apply if the tile is newly placed this turn
                if (!cell.isCommitted) {
                    when (cell.squareType) {
                        SquareType.DOUBLE_LETTER -> letterScore *= 2
                        SquareType.TRIPLE_LETTER -> letterScore *= 3
                        SquareType.CENTER -> letterScore *= 2
                        SquareType.DOUBLE_WORD -> wordMultiplier *= 2
                        SquareType.TRIPLE_WORD -> wordMultiplier *= 3
                        SquareType.NORMAL -> {}
                    }
                }
                wordLetterPoints += letterScore
            }

            val mainWord = String(wordChars.toCharArray())
            if (mainWord.length > 1) {
                if (!isWordValid(mainWord)) {
                    return RefereeResult(false, 0, listOf(mainWord), "'$mainWord' is not a valid English word.")
                }
                formedWords.add(mainWord)
                totalScore += wordLetterPoints * wordMultiplier
            }
        } else {
            val c = cols.first()
            val minRow = uncommittedCells.minOf { it.row }
            val maxRow = uncommittedCells.maxOf { it.row }

            // Check no gaps
            for (r in minRow..maxRow) {
                val cell = grid[r][c]
                if (cell?.tile == null) {
                    return RefereeResult(false, 0, emptyList(), "Tiles cannot have empty gaps between them.")
                }
            }

            var startRow = minRow
            while (startRow > 0 && grid[startRow - 1][c]?.tile != null) startRow--
            var endRow = maxRow
            while (endRow < Board4x4.SIZE - 1 && grid[endRow + 1][c]?.tile != null) endRow++

            val wordChars = mutableListOf<Char>()
            var wordLetterPoints = 0
            var wordMultiplier = 1

            for (r in startRow..endRow) {
                val cell = grid[r][c]!!
                val t = cell.tile!!
                wordChars.add(t.letter)

                var letterScore = getLetterScore(t.letter)
                if (!cell.isCommitted) {
                    when (cell.squareType) {
                        SquareType.DOUBLE_LETTER -> letterScore *= 2
                        SquareType.TRIPLE_LETTER -> letterScore *= 3
                        SquareType.CENTER -> letterScore *= 2
                        SquareType.DOUBLE_WORD -> wordMultiplier *= 2
                        SquareType.TRIPLE_WORD -> wordMultiplier *= 3
                        SquareType.NORMAL -> {}
                    }
                }
                wordLetterPoints += letterScore
            }

            val mainWord = String(wordChars.toCharArray())
            if (mainWord.length > 1) {
                if (!isWordValid(mainWord)) {
                    return RefereeResult(false, 0, listOf(mainWord), "'$mainWord' is not a valid English word.")
                }
                formedWords.add(mainWord)
                totalScore += wordLetterPoints * wordMultiplier
            }
        }

        if (formedWords.isEmpty()) {
            return RefereeResult(false, 0, emptyList(), "Word must be at least 2 letters.")
        }

        val wordsStr = formedWords.joinToString(", ")
        return RefereeResult(true, totalScore, formedWords, "Valid word: $wordsStr for $totalScore points!")
    }
}
